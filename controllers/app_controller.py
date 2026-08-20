from typing import List, Optional
from PyQt6.QtWidgets import QMessageBox

from core.interfaces import IProcessScanner, IFirewallService, IElevationService
from core.models import ProcessItem, SystemResourceSummary, NetworkState, SocketConnection
from core.i18n import i18n
from workers.monitor_worker import ProcessMonitorWorker


class AppController:
    """
    Presenter/Controller coordinating between Data Services, Background Workers, and UI Views.
    Handles business logic without coupling GUI elements to system implementations.
    """

    def __init__(
        self,
        scanner,
        firewall: IFirewallService,
        elevation: IElevationService,
        view=None
    ):
        self.scanner = scanner
        self.firewall = firewall
        self.elevation = elevation
        self.view = view

        # Background Worker Thread
        self.worker = ProcessMonitorWorker(scanner=self.scanner, firewall=self.firewall, interval_sec=1.2)
        self.worker.data_ready.connect(self._on_data_ready)
        self.worker.error_occurred.connect(self._on_worker_error)

        # Cache of latest scanned processes
        self._latest_processes: List[ProcessItem] = []
        self._latest_sockets: List[SocketConnection] = []

    def set_view(self, view):
        """Bind UI View and connect user signals."""
        self.view = view
        self._bind_signals()

    def _bind_signals(self):
        """Wire UI interaction signals to controller handlers."""
        if not self.view:
            return

        self.view.block_requested.connect(self.handle_block_application)
        self.view.unblock_requested.connect(self.handle_unblock_application)
        self.view.unblock_all_requested.connect(self.handle_unblock_all)
        self.view.profile_applied.connect(self.handle_profile_applied)
        self.view.refresh_requested.connect(self.handle_refresh_requested)
        self.view.block_socket_requested.connect(self.handle_block_socket)

    def start(self):
        """Start the background monitoring thread."""
        self.worker.start()

    def stop(self):
        """Stop background worker safely."""
        self.worker.stop()

    def _on_data_ready(self, processes: List[ProcessItem], summary: SystemResourceSummary, sockets: List[SocketConnection]):
        """Receive updated metrics from background worker and forward to UI."""
        self._latest_processes = processes
        self._latest_sockets = sockets
        if self.view:
            self.view.update_process_list(processes)
            self.view.update_system_stats(summary, sockets)

    def _on_worker_error(self, error_msg: str):
        print(f"[AppController] Background worker error: {error_msg}")

    def handle_block_application(self, process: ProcessItem):
        """Block network for the specified application."""
        if not process.exe_path:
            return

        if not self.elevation.is_admin():
            if self.view:
                self.view.show_status_message("Cần quyền Administrator để tạo quy tắc tường lửa.", is_error=True)
            return

        success = self.firewall.block_application(process.name, process.exe_path)
        if success:
            process.network_state = NetworkState.BLOCKED
            if self.view:
                self.view.show_toast("NetManager", f"{process.display_name} · {i18n['blockedStatus']}")
                self.view.update_process_list(self._latest_processes)

    def handle_unblock_application(self, process: ProcessItem):
        """Restore network access for the specified application."""
        if not process.exe_path:
            return

        if not self.elevation.is_admin():
            if self.view:
                self.view.show_status_message("Cần quyền Administrator để xóa quy tắc tường lửa.", is_error=True)
            return

        success = self.firewall.unblock_application(process.name, process.exe_path)
        if success:
            process.network_state = NetworkState.ALLOWED
            if self.view:
                self.view.show_toast("NetManager", f"{process.display_name} · {i18n['allowed']}")
                self.view.update_process_list(self._latest_processes)

    def handle_unblock_all(self):
        """Restore network for all applications blocked by NetManager."""
        blocked_paths = self.firewall.get_all_blocked_paths()
        if not blocked_paths:
            return

        for path in list(blocked_paths):
            self.firewall.unblock_application("All", path)

        for p in self._latest_processes:
            if not p.is_system:
                p.network_state = NetworkState.ALLOWED

        if self.view:
            self.view.show_toast("NetManager", i18n["allUnblocked"])
            self.view.update_process_list(self._latest_processes)

    def handle_profile_applied(self, profile_name: str):
        """Apply targeted rules based on selected profile preset."""
        targets = []
        if profile_name == "Gaming mode":
            targets = ["onedrive.exe", "mousocoreworker.exe", "googleupdate.exe", "epicgameslauncher.exe"]
        elif profile_name == "Focus mode":
            targets = ["spotify.exe", "telegram.exe", "discord.exe", "steam.exe"]
        elif profile_name == "Strict privacy":
            targets = [p.name.lower() for p in self._latest_processes if not p.is_system]

        count = 0
        for p in self._latest_processes:
            if p.name.lower() in targets and p.exe_path:
                if self.firewall.block_application(p.name, p.exe_path):
                    p.network_state = NetworkState.BLOCKED
                    count += 1

        if self.view:
            self.view.show_toast(f"{i18n['profileApplied']}: {profile_name}", f"{count} firewall rules updated.")
            self.view.update_process_list(self._latest_processes)

    def handle_block_socket(self, socket_conn: SocketConnection):
        """Find matching process for socket and block it."""
        for p in self._latest_processes:
            if p.pid == socket_conn.pid or p.name.lower() == socket_conn.process_name.lower():
                self.handle_block_application(p)
                break

    def handle_refresh_requested(self):
        pass
