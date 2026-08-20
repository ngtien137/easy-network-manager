from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional


class ProcessCategory(Enum):
    """Categorization of Windows processes matching Task Manager groups."""
    APP = "app"
    BACKGROUND = "background"
    SYSTEM = "system"


class NetworkState(Enum):
    """Network connection status for an executable or process."""
    ALLOWED = "allowed"
    BLOCKED = "blocked"
    SYSTEM = "system"
    UNKNOWN = "unknown"


@dataclass
class SocketConnection:
    """Represents an active network socket connection (TCP/UDP)."""
    id: str
    pid: int
    process_name: str
    local_address: str
    remote_address: str
    protocol: str
    state: str
    is_blocked: bool = False


@dataclass
class ProcessItem:
    """
    Data model representing an individual process or grouped application.
    """
    pid: int
    name: str
    display_name: str
    exe_path: str
    category: ProcessCategory
    cpu_percent: float = 0.0
    memory_bytes: int = 0
    memory_percent: float = 0.0
    disk_read_speed: float = 0.0   # B/s
    disk_write_speed: float = 0.0  # B/s
    network_state: NetworkState = NetworkState.ALLOWED
    network_speed: str = "0 KB/s"
    connections_count: int = 0
    instance_count: int = 1
    child_pids: List[int] = field(default_factory=list)
    username: str = ""
    status: str = "running"
    is_system: bool = False
    icon_text: str = ""
    icon_data: Optional[bytes] = None

    @property
    def memory_mb(self) -> float:
        """Return memory usage in Megabytes."""
        return self.memory_bytes / (1024 * 1024)

    @property
    def memory_formatted(self) -> str:
        """Formatted string for memory display."""
        mb = self.memory_mb
        if mb >= 1024:
            return f"{mb / 1024:.1f} GB"
        return f"{mb:.1f} MB"

    @property
    def cpu_formatted(self) -> str:
        """Formatted string for CPU percentage."""
        if self.cpu_percent < 0.1:
            return "0.0%"
        return f"{self.cpu_percent:.1f}%"


@dataclass
class SystemResourceSummary:
    """
    Overall system resource statistics for Task Manager header.
    """
    total_cpu_percent: float = 0.0
    total_memory_percent: float = 0.0
    used_memory_gb: float = 0.0
    total_memory_gb: float = 0.0
    download_speed: str = "0 KB/s"
    upload_speed: str = "0 KB/s"
    download_bytes_sec: float = 0.0
    upload_bytes_sec: float = 0.0
    total_apps_count: int = 0
    total_background_count: int = 0
    total_blocked_count: int = 0
    total_connections_count: int = 0
