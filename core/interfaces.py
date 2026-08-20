from abc import ABC, abstractmethod
from typing import List, Set, Optional
from .models import ProcessItem, SystemResourceSummary


class IProcessScanner(ABC):
    """Abstract interface for scanning and monitoring system processes."""

    @abstractmethod
    def scan_all(self, blocked_paths: Set[str]) -> List[ProcessItem]:
        """Scan all running processes and return them categorized."""
        pass

    @abstractmethod
    def get_system_summary(self, processes: List[ProcessItem]) -> SystemResourceSummary:
        """Calculate overall system CPU/Memory summary."""
        pass

    @abstractmethod
    def terminate_process(self, pid: int) -> bool:
        """Kill/Terminate a process by PID."""
        pass


class IFirewallService(ABC):
    """Abstract interface for managing network firewall rules."""

    @abstractmethod
    def is_blocked(self, exe_path: str) -> bool:
        """Check if an executable path is blocked in firewall."""
        pass

    @abstractmethod
    def block_application(self, app_name: str, exe_path: str) -> bool:
        """Block inbound and outbound network traffic for an executable."""
        pass

    @abstractmethod
    def unblock_application(self, app_name: str, exe_path: str) -> bool:
        """Remove firewall block rules for an executable."""
        pass

    @abstractmethod
    def get_all_blocked_paths(self) -> Set[str]:
        """Retrieve set of all executable paths currently blocked by NetManager."""
        pass


class IElevationService(ABC):
    """Abstract interface for checking and requesting administrative privileges."""

    @abstractmethod
    def is_admin(self) -> bool:
        """Check if current process has Administrator privileges."""
        pass

    @abstractmethod
    def elevate(self) -> bool:
        """Relaunch the application with elevated Administrator privileges."""
        pass
