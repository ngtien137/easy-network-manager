from typing import List, Optional
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QTreeWidget, QTreeWidgetItem, QHeaderView,
    QCheckBox, QFrame, QScrollArea
)
from PyQt6.QtCore import Qt, pyqtSignal, QSettings
from PyQt6.QtGui import QFont

from core.models import ProcessItem, ProcessCategory, NetworkState, SystemResourceSummary
from core.i18n import i18n
from ui.components.metric_card import MetricCard
from ui.components.status_badge import StatusBadge
from ui.modals.process_inspector import ProcessInspectorModal


class ProcessesView(QWidget):
    """
    Main Process Explorer View matching the Fluent Control Room Web Demo layout.
    """

    block_requested = pyqtSignal(object)
    unblock_requested = pyqtSignal(object)
    unblock_all_requested = pyqtSignal()
    refresh_requested = pyqtSignal()
    view_traffic_requested = pyqtSignal(object)

    def __init__(self, is_admin: bool = False, parent=None):
        super().__init__(parent)
        self.is_admin = is_admin
        self._processes: List[ProcessItem] = []
        self._filter_mode = "all"  # 'all', 'app', 'blocked'
        self._search_query = ""
        self.settings = QSettings("NetManagerApp", "NetManager")

        self._setup_ui()
        i18n.language_changed.connect(self.retranslate)

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(28, 24, 28, 20)
        main_layout.setSpacing(16)

        # 1. Page Heading
        heading_layout = QHBoxLayout()
        title_box = QVBoxLayout()
        title_box.setSpacing(4)

        self.lbl_eyebrow = QLabel("LIVE PROCESS TELEMETRY")
        self.lbl_eyebrow.setObjectName("Eyebrow")

        self.lbl_title = QLabel(i18n["overview"])
        self.lbl_title.setObjectName("PageTitle")

        self.lbl_sub = QLabel(i18n["overviewSub"])
        self.lbl_sub.setObjectName("PageSubtitle")

        title_box.addWidget(self.lbl_eyebrow)
        title_box.addWidget(self.lbl_title)
        title_box.addWidget(self.lbl_sub)
        heading_layout.addLayout(title_box, stretch=1)

        self.btn_refresh = QPushButton(f"🔄 {i18n['refresh']}")
        self.btn_refresh.setObjectName("QuietBtn")
        self.btn_refresh.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_refresh.clicked.connect(self.refresh_requested.emit)
        heading_layout.addWidget(self.btn_refresh, alignment=Qt.AlignmentFlag.AlignTop)

        main_layout.addLayout(heading_layout)

        # 2. KPI Metric Cards Grid
        kpi_layout = QHBoxLayout()
        kpi_layout.setSpacing(12)

        self.card_cpu = MetricCard(i18n["cpu"], "⚡", "#20b8f2")
        self.card_ram = MetricCard(i18n["memory"], "💾", "#bdc8d4")
        self.card_speed = MetricCard(i18n["speed"], "🌐", "#41e6a5")
        self.card_blocked = MetricCard(i18n["blockedApps"], "🛡️", "#ff6868")

        kpi_layout.addWidget(self.card_cpu)
        kpi_layout.addWidget(self.card_ram)
        kpi_layout.addWidget(self.card_speed)
        kpi_layout.addWidget(self.card_blocked)
        main_layout.addLayout(kpi_layout)

        # 3. Table Panel (Toolbar + Process Tree)
        self.table_panel = QFrame()
        self.table_panel.setObjectName("TablePanel")
        panel_layout = QVBoxLayout(self.table_panel)
        panel_layout.setContentsMargins(1, 1, 1, 1)
        panel_layout.setSpacing(0)

        # Process Toolbar
        toolbar = QFrame()
        toolbar.setStyleSheet("border-bottom: 1px solid rgba(213, 225, 240, 0.10); padding: 10px 14px;")
        tool_layout = QHBoxLayout(toolbar)
        tool_layout.setContentsMargins(0, 0, 0, 0)
        tool_layout.setSpacing(12)

        self.table_search = QLineEdit()
        self.table_search.setObjectName("TableSearch")
        self.table_search.setPlaceholderText(i18n["search"])
        self.table_search.setFixedWidth(320)
        self.table_search.textChanged.connect(self._on_search_changed)
        tool_layout.addWidget(self.table_search)

        # Filter Tabs
        filter_frame = QFrame()
        filter_frame.setObjectName("FilterTabsFrame")
        f_layout = QHBoxLayout(filter_frame)
        f_layout.setContentsMargins(3, 3, 3, 3)
        f_layout.setSpacing(4)

        self.btn_f_all = QPushButton(i18n["all"])
        self.btn_f_all.setObjectName("FilterTabBtn")
        self.btn_f_all.setProperty("active", "true")
        self.btn_f_all.clicked.connect(lambda: self._set_filter("all"))

        self.btn_f_apps = QPushButton(i18n["apps"])
        self.btn_f_apps.setObjectName("FilterTabBtn")
        self.btn_f_apps.clicked.connect(lambda: self._set_filter("app"))

        self.btn_f_blocked = QPushButton(i18n["blocked"])
        self.btn_f_blocked.setObjectName("FilterTabBtn")
        self.btn_f_blocked.clicked.connect(lambda: self._set_filter("blocked"))

        f_layout.addWidget(self.btn_f_all)
        f_layout.addWidget(self.btn_f_apps)
        f_layout.addWidget(self.btn_f_blocked)
        tool_layout.addWidget(filter_frame)

        tool_layout.addStretch(1)

        self.btn_unblock_all = QPushButton(f"🛡️ {i18n['unblockAll']}")
        self.btn_unblock_all.setObjectName("PrimaryActionBtn")
        self.btn_unblock_all.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_unblock_all.clicked.connect(self.unblock_all_requested.emit)
        tool_layout.addWidget(self.btn_unblock_all)

        panel_layout.addWidget(toolbar)

        # Process Tree Widget
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels([
            i18n["process"], i18n["networkStatus"], i18n["usage"],
            i18n["ram"], i18n["trafficCol"], "PID", i18n["action"]
        ])
        
        # Configure generous column widths to avoid any button clipping
        self.tree.header().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.tree.header().setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        self.tree.header().setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        self.tree.header().setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        self.tree.header().setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        self.tree.header().setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)
        self.tree.header().setSectionResizeMode(6, QHeaderView.ResizeMode.Fixed)

        self.tree.setColumnWidth(1, 120)  # Status badge
        self.tree.setColumnWidth(2, 75)   # CPU
        self.tree.setColumnWidth(3, 95)   # RAM
        self.tree.setColumnWidth(4, 95)   # Traffic
        self.tree.setColumnWidth(5, 75)   # PID
        self.tree.setColumnWidth(6, 175)  # Action (••• + Block button)

        self.tree.setIndentation(16)
        self.tree.setAnimated(True)
        self.tree.setRootIsDecorated(True)

        self.apps_group = QTreeWidgetItem(self.tree, [f"▼  {i18n['appsGroup']} (0)"])
        self.bg_group = QTreeWidgetItem(self.tree, [f"▼  {i18n['backgroundGroup']} (0)"])
        for g in (self.apps_group, self.bg_group):
            g.setExpanded(True)
            g.setFlags(Qt.ItemFlag.ItemIsEnabled)
            font = QFont()
            font.setBold(True)
            font.setPointSize(9)
            g.setFont(0, font)

        panel_layout.addWidget(self.tree, stretch=1)
        main_layout.addWidget(self.table_panel, stretch=1)

        # 4. Footer
        footer_layout = QHBoxLayout()
        self.chk_restore = QCheckBox(i18n["restore"])
        self.chk_restore.setChecked(self.settings.value("auto_unblock_on_exit", True, type=bool))
        self.chk_restore.toggled.connect(lambda c: self.settings.setValue("auto_unblock_on_exit", c))
        self.chk_restore.setStyleSheet("color: #8e99a9; font-size: 12px;")

        footer_layout.addWidget(self.chk_restore)
        footer_layout.addStretch(1)

        self.lbl_admin_status = QLabel(f"🛡️ {i18n['admin']}")
        self.lbl_admin_status.setObjectName("AdminChip")
        footer_layout.addWidget(self.lbl_admin_status)

        self.lbl_running_count = QLabel(f"0 {i18n['running']}")
        self.lbl_running_count.setStyleSheet("color: #667181; font-size: 12px;")
        footer_layout.addWidget(self.lbl_running_count)

        main_layout.addLayout(footer_layout)

        self._tree_items = {}

    def _set_filter(self, mode: str):
        self._filter_mode = mode
        for btn, m in [(self.btn_f_all, "all"), (self.btn_f_apps, "app"), (self.btn_f_blocked, "blocked")]:
            btn.setProperty("active", "true" if m == mode else "false")
            btn.style().unpolish(btn)
            btn.style().polish(btn)
        self._render_processes()

    def _on_search_changed(self, text: str):
        self._search_query = text.strip().lower()
        self._render_processes()

    def set_search_query(self, query: str):
        self.table_search.setText(query)

    def update_processes(self, processes: List[ProcessItem]):
        self._processes = processes
        self._render_processes()

    def _render_processes(self):
        current_keys = set()
        apps_count = 0
        bg_count = 0

        filtered = []
        for p in self._processes:
            # Search
            if self._search_query:
                q = self._search_query
                match = q in p.name.lower() or q in p.display_name.lower() or q in str(p.pid) or q in p.exe_path.lower()
                if not match:
                    continue

            # Category filter
            if self._filter_mode == "app" and p.category != ProcessCategory.APP:
                continue
            if self._filter_mode == "blocked" and p.network_state != NetworkState.BLOCKED:
                continue

            filtered.append(p)

        for p in filtered:
            key = p.exe_path.lower() if p.exe_path else f"pid_{p.pid}"
            current_keys.add(key)

            if p.category == ProcessCategory.APP:
                apps_count += 1
                parent_group = self.apps_group
            else:
                bg_count += 1
                parent_group = self.bg_group

            display_name = f"{p.display_name} ({p.instance_count})" if p.instance_count > 1 else p.display_name

            if key in self._tree_items:
                tree_item = self._tree_items[key]
                tree_item.setText(0, f"  {display_name}")
                tree_item.setText(2, p.cpu_formatted)
                tree_item.setText(3, p.memory_formatted)
                tree_item.setText(4, p.network_speed)
                tree_item.setText(5, str(p.pid))
                tree_item.setData(0, Qt.ItemDataRole.UserRole, p)

                # Update badge
                badge = self.tree.itemWidget(tree_item, 1)
                if isinstance(badge, StatusBadge):
                    badge.set_state(p.network_state)

                # Update actions
                action_box = self.tree.itemWidget(tree_item, 6)
                if action_box:
                    self._update_action_buttons(action_box, p)
            else:
                tree_item = QTreeWidgetItem(parent_group, [
                    f"  {display_name}", "", p.cpu_formatted, p.memory_formatted, p.network_speed, str(p.pid), ""
                ])
                tree_item.setData(0, Qt.ItemDataRole.UserRole, p)
                self._tree_items[key] = tree_item

                # Setup Badge
                badge = StatusBadge(p.network_state)
                self.tree.setItemWidget(tree_item, 1, badge)

                # Setup Action Container
                action_widget = self._create_action_widget(p)
                self.tree.setItemWidget(tree_item, 6, action_widget)

        # Remove dead items
        dead_keys = [k for k in self._tree_items.keys() if k not in current_keys]
        for k in dead_keys:
            item = self._tree_items.pop(k)
            parent = item.parent()
            if parent:
                parent.removeChild(item)

        # Update headers
        self.apps_group.setText(0, f"▼  {i18n['appsGroup']} ({apps_count})")
        self.bg_group.setText(0, f"▼  {i18n['backgroundGroup']} ({bg_count})")
        self.lbl_running_count.setText(f"{len(self._processes)} {i18n['running']}")

    def _create_action_widget(self, process: ProcessItem) -> QWidget:
        container = QWidget()
        container.setFixedHeight(34)
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 8, 0)
        layout.setSpacing(6)
        layout.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        # Details button (...)
        btn_details = QPushButton("•••")
        btn_details.setObjectName("QuietBtn")
        btn_details.setFixedSize(32, 28)
        btn_details.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_details.clicked.connect(lambda: self._open_inspector(process))
        layout.addWidget(btn_details)

        # Rule Button
        btn_rule = QPushButton()
        btn_rule.setFixedHeight(28)
        btn_rule.setMinimumWidth(110)
        btn_rule.setCursor(Qt.CursorShape.PointingHandCursor)
        self._configure_rule_button(btn_rule, process)
        btn_rule.clicked.connect(lambda _, b=btn_rule, p=process: self._toggle_process_network(p, b))
        layout.addWidget(btn_rule)

        return container

    def _configure_rule_button(self, btn: QPushButton, process: ProcessItem):
        if process.is_system:
            btn.setText(f"🔒 {i18n['locked']}")
            btn.setEnabled(False)
            btn.setStyleSheet("""
                QPushButton {
                    background: rgba(255, 255, 255, 0.03);
                    color: #5f6976;
                    border: 1px solid rgba(213,225,240,0.1);
                    border-radius: 6px;
                    padding: 3px 8px;
                    font-size: 11px;
                    font-weight: 600;
                }
            """)
        elif not process.exe_path:
            btn.setText("N/A")
            btn.setEnabled(False)
        elif process.network_state == NetworkState.BLOCKED:
            btn.setText(f"🔓 {i18n['unblock']}")
            btn.setEnabled(True)
            btn.setStyleSheet("""
                QPushButton {
                    background: rgba(65, 230, 165, 0.12);
                    color: #84edca;
                    border: 1px solid rgba(65, 230, 165, 0.35);
                    border-radius: 6px;
                    padding: 3px 10px;
                    font-size: 11px;
                    font-weight: 700;
                }
                QPushButton:hover {
                    background: rgba(65, 230, 165, 0.22);
                }
            """)
        else:
            btn.setText(f"🚫 {i18n['block']}")
            btn.setEnabled(True)
            btn.setStyleSheet("""
                QPushButton {
                    background: rgba(255, 104, 104, 0.12);
                    color: #ff9f9f;
                    border: 1px solid rgba(255, 104, 104, 0.35);
                    border-radius: 6px;
                    padding: 3px 10px;
                    font-size: 11px;
                    font-weight: 700;
                }
                QPushButton:hover {
                    background: rgba(255, 104, 104, 0.22);
                    color: #ffffff;
                }
            """)

    def _update_action_buttons(self, container: QWidget, process: ProcessItem):
        buttons = container.findChildren(QPushButton)
        if len(buttons) >= 2:
            self._configure_rule_button(buttons[1], process)

    def _open_inspector(self, process: ProcessItem):
        modal = ProcessInspectorModal(process, self)
        modal.block_requested.connect(self.block_requested)
        modal.unblock_requested.connect(self.unblock_requested)
        modal.view_traffic_requested.connect(self.view_traffic_requested)
        modal.exec()

    def _toggle_process_network(self, process: ProcessItem, btn: QPushButton = None):
        if btn:
            btn.setText("⏳ ...")
            btn.setEnabled(False)
            btn.setStyleSheet("""
                QPushButton {
                    background: rgba(32, 184, 242, 0.15);
                    color: #b8efff;
                    border: 1px solid #20b8f2;
                    border-radius: 6px;
                    padding: 3px 10px;
                    font-size: 11px;
                    font-weight: 700;
                }
            """)
        if process.network_state == NetworkState.BLOCKED:
            self.unblock_requested.emit(process)
        else:
            self.block_requested.emit(process)

    def update_system_stats(self, summary: SystemResourceSummary):
        self.card_cpu.set_data(f"{summary.total_cpu_percent}%", "Real-time CPU load", summary.total_cpu_percent)
        self.card_ram.set_data(f"{summary.used_memory_gb:.1f} GB", f"of {summary.total_memory_gb:.1f} GB · {summary.total_memory_percent}% used", summary.total_memory_percent)
        self.card_speed.set_data(summary.download_speed, f"↓ {summary.download_speed} · ↑ {summary.upload_speed}", min(summary.download_bytes_sec / (1024*1024*10) * 100, 100))
        blocked_pct = (summary.total_blocked_count / max(summary.total_apps_count + summary.total_background_count, 1)) * 100
        self.card_blocked.set_data(str(summary.total_blocked_count), f"{summary.total_apps_count + summary.total_background_count - summary.total_blocked_count} permitted", blocked_pct)

    def retranslate(self):
        self.lbl_title.setText(i18n["overview"])
        self.lbl_sub.setText(i18n["overviewSub"])
        self.btn_refresh.setText(f"🔄 {i18n['refresh']}")
        self.card_cpu.set_title(i18n["cpu"])
        self.card_ram.set_title(i18n["memory"])
        self.card_speed.set_title(i18n["speed"])
        self.card_blocked.set_title(i18n["blockedApps"])
        self.table_search.setPlaceholderText(i18n["search"])
        self.btn_f_all.setText(i18n["all"])
        self.btn_f_apps.setText(i18n["apps"])
        self.btn_f_blocked.setText(i18n["blocked"])
        self.btn_unblock_all.setText(f"🛡️ {i18n['unblockAll']}")
        self.tree.setHeaderLabels([
            i18n["process"], i18n["networkStatus"], i18n["usage"],
            i18n["ram"], i18n["trafficCol"], "PID", i18n["action"]
        ])
        self.chk_restore.setText(i18n["restore"])
        self.lbl_admin_status.setText(f"🛡️ {i18n['admin']}")
        self._render_processes()
