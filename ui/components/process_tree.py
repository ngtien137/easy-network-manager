import os
import subprocess
from typing import List, Dict, Optional

from PyQt6.QtWidgets import (
    QTreeWidget, QTreeWidgetItem, QHeaderView, QMenu,
    QWidget, QHBoxLayout, QPushButton, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor, QAction

from core.models import ProcessItem, ProcessCategory, NetworkState
from .status_badge import StatusBadge


class ProcessTreeWidget(QTreeWidget):
    """
    Hierarchical Tree View matching Windows 11 Task Manager.
    Displays grouped Apps and Background processes with real-time metrics and network actions.
    """

    block_requested = pyqtSignal(object)       # (ProcessItem)
    unblock_requested = pyqtSignal(object)     # (ProcessItem)
    terminate_requested = pyqtSignal(int)      # (PID)

    def __init__(self, parent=None):
        super().__init__(parent)

        # Setup column headers
        self.setHeaderLabels(["Name", "Network Status", "CPU", "Memory", "PID", "Quick Action"])
        self.header().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.header().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.header().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.header().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.header().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        self.header().setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)

        self.setAnimated(True)
        self.setIndentation(20)
        self.setRootIsDecorated(True)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)

        # Top-level group headers
        self.apps_group_item = QTreeWidgetItem(self, ["Apps (0)"])
        self.bg_group_item = QTreeWidgetItem(self, ["Background processes (0)"])

        font = QFont()
        font.setBold(True)
        font.setPointSize(10)
        for group in (self.apps_group_item, self.bg_group_item):
            group.setFont(0, font)
            group.setExpanded(True)
            group.setFlags(Qt.ItemFlag.ItemIsEnabled)

        # Internal tracking dictionary: key = exe_path or pid -> QTreeWidgetItem
        self._tree_items: Dict[str, QTreeWidgetItem] = {}
        self._search_filter = ""
        self._filter_mode = "all"  # "all", "apps", "blocked"

    def update_processes(self, processes: List[ProcessItem]):
        """Update tree rows with the latest process snapshot."""
        current_keys = set()
        apps_count = 0
        bg_count = 0

        # Filter processes based on search query and filter mode
        filtered_processes = []
        for p in processes:
            # Search filter
            if self._search_filter:
                q = self._search_filter.lower()
                name_match = q in p.name.lower() or q in p.display_name.lower()
                pid_match = q in str(p.pid)
                exe_match = q in p.exe_path.lower()
                if not (name_match or pid_match or exe_match):
                    continue

            # Tab/Category filter
            if self._filter_mode == "apps" and p.category != ProcessCategory.APP:
                continue
            if self._filter_mode == "blocked" and p.network_state != NetworkState.BLOCKED:
                continue

            filtered_processes.append(p)

        for p in filtered_processes:
            key = p.exe_path.lower() if p.exe_path else f"pid_{p.pid}"
            current_keys.add(key)

            if p.category == ProcessCategory.APP:
                apps_count += 1
                parent_group = self.apps_group_item
            else:
                bg_count += 1
                parent_group = self.bg_group_item

            # Format name with instance count
            if p.instance_count > 1:
                display_title = f"{p.display_name} ({p.instance_count})"
            else:
                display_title = p.display_name

            # Check if item exists in tree
            if key in self._tree_items:
                tree_item = self._tree_items[key]
                # Update text
                tree_item.setText(0, display_title)
                tree_item.setText(2, p.cpu_formatted)
                tree_item.setText(3, p.memory_formatted)
                tree_item.setText(4, str(p.pid))
                tree_item.setData(0, Qt.ItemDataRole.UserRole, p)

                # Update status badge
                badge = self.itemWidget(tree_item, 1)
                if isinstance(badge, StatusBadge):
                    badge.set_state(p.network_state)

                # Update action button
                action_container = self.itemWidget(tree_item, 5)
                if action_container:
                    btn = action_container.findChild(QPushButton)
                    if btn:
                        self._configure_action_button(btn, p)
            else:
                # Create new TreeWidgetItem
                tree_item = QTreeWidgetItem(parent_group, [
                    display_title,
                    "",
                    p.cpu_formatted,
                    p.memory_formatted,
                    str(p.pid),
                    ""
                ])
                tree_item.setData(0, Qt.ItemDataRole.UserRole, p)
                self._tree_items[key] = tree_item

                # Setup Status Badge
                badge = StatusBadge(p.network_state)
                self.setItemWidget(tree_item, 1, badge)

                # Setup Action Button
                action_widget = self._create_action_widget(p)
                self.setItemWidget(tree_item, 5, action_widget)

        # Remove dead processes
        dead_keys = [k for k in self._tree_items.keys() if k not in current_keys]
        for k in dead_keys:
            item = self._tree_items.pop(k)
            parent = item.parent()
            if parent:
                parent.removeChild(item)

        # Update header labels with counts
        self.apps_group_item.setText(0, f"Apps ({apps_count})")
        self.bg_group_item.setText(0, f"Background processes ({bg_count})")

    def _create_action_widget(self, process: ProcessItem) -> QWidget:
        """Create the action button container for the tree row."""
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(4, 2, 4, 2)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        btn = QPushButton()
        btn.setFixedHeight(26)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._configure_action_button(btn, process)

        btn.clicked.connect(lambda: self._handle_button_action(process))
        layout.addWidget(btn)
        return container

    def _configure_action_button(self, btn: QPushButton, process: ProcessItem):
        """Update button style based on network state."""
        if not process.exe_path:
            btn.setText("N/A")
            btn.setEnabled(False)
            btn.setObjectName("")
            return

        btn.setEnabled(True)
        if process.network_state == NetworkState.BLOCKED:
            btn.setText("🔓 Unblock")
            btn.setObjectName("SuccessBtn")
            btn.setToolTip("Click to restore network access for this application")
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #15803d;
                    color: #ffffff;
                    border: 1px solid #16a34a;
                    border-radius: 4px;
                    padding: 2px 10px;
                    font-weight: 600;
                    font-size: 11px;
                }
                QPushButton:hover {
                    background-color: #16a34a;
                }
            """)
        else:
            btn.setText("🚫 Block Net")
            btn.setObjectName("DangerBtn")
            btn.setToolTip("Click to block all network traffic for this application")
            btn.setStyleSheet("""
                QPushButton {
                    background-color: rgba(220, 38, 38, 0.2);
                    color: #f87171;
                    border: 1px solid rgba(220, 38, 38, 0.4);
                    border-radius: 4px;
                    padding: 2px 10px;
                    font-weight: 600;
                    font-size: 11px;
                }
                QPushButton:hover {
                    background-color: #dc2626;
                    color: #ffffff;
                }
            """)

    def _handle_button_action(self, process: ProcessItem):
        """Handle click on the action button."""
        if process.network_state == NetworkState.BLOCKED:
            self.unblock_requested.emit(process)
        else:
            self.block_requested.emit(process)

    def set_search_query(self, query: str):
        """Apply search filter string."""
        self._search_filter = query.strip()

    def set_filter_mode(self, mode: str):
        """Set filter mode ('all', 'apps', 'blocked')."""
        self._filter_mode = mode

    def _show_context_menu(self, position):
        """Display right-click context menu."""
        item = self.itemAt(position)
        if not item or item in (self.apps_group_item, self.bg_group_item):
            return

        process: Optional[ProcessItem] = item.data(0, Qt.ItemDataRole.UserRole)
        if not process:
            return

        menu = QMenu(self)

        # Network Toggle Action
        if process.exe_path:
            if process.network_state == NetworkState.BLOCKED:
                action_net = menu.addAction("🟢 Allow Network Access (Unblock)")
                action_net.triggered.connect(lambda: self.unblock_requested.emit(process))
            else:
                action_net = menu.addAction("🔴 Block Network Access (Kill-switch)")
                action_net.triggered.connect(lambda: self.block_requested.emit(process))

        menu.addSeparator()

        # End Task Action
        action_kill = menu.addAction("⛔ End Task")
        action_kill.triggered.connect(lambda: self.terminate_requested.emit(process.pid))

        # Open File Location
        if process.exe_path and os.path.exists(process.exe_path):
            action_open_dir = menu.addAction("📁 Open File Location")
            action_open_dir.triggered.connect(lambda: self._open_file_location(process.exe_path))

        menu.exec(self.viewport().mapToGlobal(position))

    def _open_file_location(self, exe_path: str):
        """Open Windows Explorer highlighting the executable."""
        try:
            subprocess.run(f'explorer.exe /select,"{exe_path}"', shell=True)
        except Exception as e:
            print(f"[ProcessTree] Failed to open explorer: {e}")
