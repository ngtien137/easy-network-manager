import time
from typing import Set
from PyQt6.QtCore import QThread, pyqtSignal

from core.interfaces import IProcessScanner, IFirewallService
from core.models import ProcessItem, SystemResourceSummary, SocketConnection


class ProcessMonitorWorker(QThread):
    """
    Background worker thread that periodically polls system processes,
    CPU/RAM metrics, network throughput, sockets, and firewall block states.
    """

    # Signals emitted to UI: (List[ProcessItem], SystemResourceSummary, List[SocketConnection])
    data_ready = pyqtSignal(list, object, list)
    error_occurred = pyqtSignal(str)

    def __init__(self, scanner, firewall: IFirewallService, interval_sec: float = 1.2, parent=None):
        super().__init__(parent)
        self.scanner = scanner
        self.firewall = firewall
        self.interval_sec = interval_sec
        self._is_running = True
        self._is_paused = False

    def run(self):
        """Worker main loop running in separate thread."""
        while self._is_running:
            if not self._is_paused:
                try:
                    # 1. Fetch current blocked paths
                    blocked_paths: Set[str] = self.firewall.get_all_blocked_paths()

                    # 2. Scan processes
                    processes = self.scanner.scan_all(blocked_paths)

                    # 3. Calculate system resource summary
                    summary = self.scanner.get_system_summary(processes)

                    # 4. Fetch active sockets if method available
                    sockets = []
                    if hasattr(self.scanner, 'get_active_sockets'):
                        sockets = self.scanner.get_active_sockets(blocked_paths)

                    # 5. Emit data to UI thread
                    self.data_ready.emit(processes, summary, sockets)

                except Exception as e:
                    self.error_occurred.emit(str(e))

            # Sleep in small chunks
            sleep_chunks = int(self.interval_sec * 10)
            for _ in range(sleep_chunks):
                if not self._is_running:
                    break
                time.sleep(0.1)

    def pause(self):
        self._is_paused = True

    def resume(self):
        self._is_paused = False

    def stop(self):
        self._is_running = False
        self.wait(2000)
