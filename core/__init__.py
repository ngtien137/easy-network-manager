"""
Core package for NetworkManager application.
Contains business logic, data models, interfaces, and system services.
"""

from .models import ProcessItem, ProcessCategory, NetworkState, SystemResourceSummary
from .interfaces import IProcessScanner, IFirewallService, IElevationService
from .elevation import WindowsElevationService
from .firewall_service import WindowsFirewallService
from .process_scanner import WindowsProcessScanner

__all__ = [
    "ProcessItem",
    "ProcessCategory",
    "NetworkState",
    "SystemResourceSummary",
    "IProcessScanner",
    "IFirewallService",
    "IElevationService",
    "WindowsElevationService",
    "WindowsFirewallService",
    "WindowsProcessScanner",
]
