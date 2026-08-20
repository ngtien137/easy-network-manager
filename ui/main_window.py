import os
import sys
from typing import List, Optional
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QStackedWidget, QMessageBox, QSystemTrayIcon, QMenu, QApplication
)
from PyQt6.QtCore import Qt, pyqtSignal, QSettings
from PyQt6.QtGui import QIcon, QAction

from core.models import ProcessItem, SystemResourceSummary, SocketConnection
from core.i18n import i18n
from ui.theme import ThemeManager
from ui.components.sidebar import Sidebar
from ui.components.topbar import Topbar
from ui.views.processes_view import ProcessesView
from ui.views.traffic_view import TrafficView
from ui.views.profiles_view import ProfilesView
from ui.views.settings_view import SettingsView
from ui.modals.exit_dialog import ExitCleanupDialog


def get_resource_path(relative_path: str) -> str:
    """Get absolute path to resource, works for dev and for PyInstaller bundle."""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_dir, relative_path)


class MainWindow(QMainWindow):
    """
    Main Application Window with Sidebar navigation and multi-view stacked workflow.
    Matches the exact layout, theme, and UX of the Fluent Control Room Web Demo.
    """

    block_requested = pyqtSignal(object)
    unblock_requested = pyqtSignal(object)
    unblock_all_requested = pyqtSignal()
    profile_applied = pyqtSignal(str)
    refresh_requested = pyqtSignal()
    block_socket_requested = pyqtSignal(object)

    def __init__(self, is_admin: bool = False, parent=None):
        super().__init__(parent)
        self.is_admin = is_admin
        self.current_theme = "dark"
        self.settings = QSettings("NetManagerApp", "NetManager")

        # Initialize language preference (default English)
        saved_lang = self.settings.value("language", "en", type=str)
        i18n.set_language(saved_lang)

        self.setWindowTitle("Kayzit NetManager — Windows Process & Network Firewall")
        self.resize(1150, 760)
        self.setMinimumSize(950, 600)

        # Set Window Icon
        icon_path = get_resource_path(os.path.join("resources", "icon.png"))
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        self._setup_ui()
        self._setup_system_tray()

    def _setup_ui(self):
        root_widget = QWidget(self)
        self.setCentralWidget(root_widget)
        root_layout = QHBoxLayout(root_widget)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # 1. Left Sidebar
        self.sidebar = Sidebar(self)
        self.sidebar.page_changed.connect(self._on_page_navigated)
        root_layout.addWidget(self.sidebar)

        # 2. Right Workspace (Topbar + Stacked Views)
        workspace = QWidget()
        ws_layout = QVBoxLayout(workspace)
        ws_layout.setContentsMargins(0, 0, 0, 0)
        ws_layout.setSpacing(0)

        # Topbar
        self.topbar = Topbar(is_admin=self.is_admin, current_theme=self.current_theme, parent=self)
        self.topbar.search_changed.connect(self._on_search_changed)
        self.topbar.theme_toggled.connect(self._toggle_theme)
        self.topbar.language_toggled.connect(self._on_language_changed)
        ws_layout.addWidget(self.topbar)

        # Stacked Views Area
        self.stack = QStackedWidget()

        # View 0: Processes
        self.view_processes = ProcessesView(is_admin=self.is_admin, parent=self)
        self.view_processes.block_requested.connect(self.block_requested)
        self.view_processes.unblock_requested.connect(self.unblock_requested)
        self.view_processes.unblock_all_requested.connect(self.unblock_all_requested)
        self.view_processes.refresh_requested.connect(self.refresh_requested)
        self.view_processes.view_traffic_requested.connect(lambda p: self._navigate_to_page("traffic"))
        self.stack.addWidget(self.view_processes)

        # View 1: Traffic
        self.view_traffic = TrafficView(parent=self)
        self.view_traffic.block_socket_requested.connect(self.block_socket_requested)
        self.view_traffic.refresh_requested.connect(self.refresh_requested)
        self.stack.addWidget(self.view_traffic)

        # View 2: Profiles
        self.view_profiles = ProfilesView(parent=self)
        self.view_profiles.profile_applied.connect(self.profile_applied)
        self.stack.addWidget(self.view_profiles)

        # View 3: Settings
        self.view_settings = SettingsView(current_theme=self.current_theme, parent=self)
        self.view_settings.theme_changed.connect(self._set_theme)
        self.view_settings.reset_defaults_requested.connect(self.unblock_all_requested)
        self.stack.addWidget(self.view_settings)

        ws_layout.addWidget(self.stack, stretch=1)
        root_layout.addWidget(workspace, stretch=1)

    def _setup_system_tray(self):
        """Setup Windows System Tray icon."""
        self.tray_icon = QSystemTrayIcon(self)
        icon_path = get_resource_path(os.path.join("resources", "icon.png"))
        if os.path.exists(icon_path):
            self.tray_icon.setIcon(QIcon(icon_path))
        self.tray_icon.setToolTip("Kayzit NetManager — Control Room")

        tray_menu = QMenu()
        act_open = tray_menu.addAction("⚡ Open Kayzit NetManager")
        act_open.triggered.connect(self.restore_and_activate)
        act_unblock = tray_menu.addAction("🔓 Unblock All Applications")
        act_unblock.triggered.connect(self.unblock_all_requested.emit)
        tray_menu.addSeparator()
        act_exit = tray_menu.addAction("✕ Exit")
        act_exit.triggered.connect(self._force_exit)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self._on_tray_activated)
        self.tray_icon.show()

    def _on_tray_activated(self, reason):
        if reason in (QSystemTrayIcon.ActivationReason.Trigger, QSystemTrayIcon.ActivationReason.DoubleClick):
            self.restore_and_activate()

    def restore_and_activate(self):
        """Restore window from tray / minimized state and bring to front."""
        if not self.isVisible():
            self.show()
        if self.isMinimized():
            self.showNormal()
        self.raise_()
        self.activateWindow()

        # Windows Win32 API force foreground window
        try:
            import ctypes
            hwnd = int(self.winId())
            ctypes.windll.user32.ShowWindow(hwnd, 9) # SW_RESTORE
            ctypes.windll.user32.SetForegroundWindow(hwnd)
        except Exception:
            pass

    def _on_page_navigated(self, page_id: str):
        page_map = {
            "processes": 0,
            "traffic": 1,
            "profiles": 2,
            "settings": 3
        }
        self.stack.setCurrentIndex(page_map.get(page_id, 0))

    def _navigate_to_page(self, page_id: str):
        self.sidebar._on_nav_clicked(page_id)

    def _on_search_changed(self, query: str):
        self.view_processes.set_search_query(query)
        if self.stack.currentIndex() != 0:
            self._navigate_to_page("processes")

    def _toggle_theme(self):
        new_theme = "light" if self.current_theme == "dark" else "dark"
        self._set_theme(new_theme)

    def _set_theme(self, theme: str):
        self.current_theme = theme
        app = QApplication.instance()
        if app:
            ThemeManager.apply_theme(app, theme)
        self.topbar.current_theme = theme
        self.view_settings.current_theme = theme

    def _on_language_changed(self, lang: str):
        self.settings.setValue("language", lang)

    def update_process_list(self, processes: List[ProcessItem]):
        self.sidebar.update_process_count(len(processes))
        self.view_processes.update_processes(processes)

    def update_system_stats(self, summary: SystemResourceSummary, sockets: List[SocketConnection] = None):
        self.view_processes.update_system_stats(summary)
        if sockets is not None:
            self.view_traffic.update_telemetry(summary, sockets)
        self.view_profiles.set_active_profile(self.view_profiles._current_profile, summary.total_blocked_count)

    def show_status_message(self, message: str, is_error: bool = False):
        if is_error:
            QMessageBox.warning(self, "NetManager", message)

    def show_toast(self, title: str, message: str):
        """Show non-blocking system tray balloon / notification."""
        if self.tray_icon.isVisible():
            self.tray_icon.showMessage(title, message, QSystemTrayIcon.MessageIcon.Information, 2500)

    def closeEvent(self, event):
        """Handle window close event (System Tray vs Auto-restore)."""
        minimize_to_tray = self.settings.value("minimize_to_tray", True, type=bool)
        auto_unblock = self.settings.value("auto_unblock_on_exit", True, type=bool)

        if minimize_to_tray and self.tray_icon.isVisible() and not getattr(self, '_is_quitting', False):
            self.hide()
            self.show_toast("Kayzit NetManager", "App running in system tray.")
            event.ignore()
            return

        if auto_unblock:
            dialog = ExitCleanupDialog(self)
            dialog.show()
            QApplication.processEvents()
            self.unblock_all_requested.emit()
            dialog.close()

        event.accept()

    def _force_exit(self):
        self._is_quitting = True
        auto_unblock = self.settings.value("auto_unblock_on_exit", True, type=bool)
        if auto_unblock:
            dialog = ExitCleanupDialog(None)
            dialog.show()
            QApplication.processEvents()
            self.unblock_all_requested.emit()
            dialog.close()
        QApplication.quit()
