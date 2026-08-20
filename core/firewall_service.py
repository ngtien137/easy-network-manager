import os
import hashlib
import subprocess
import re
from typing import Set
from .interfaces import IFirewallService

# Windows flag to suppress CMD window popup
CREATE_NO_WINDOW = 0x08000000 if os.name == 'nt' else 0


class WindowsFirewallService(IFirewallService):
    """
    Manages Windows Defender Firewall rules for blocking/unblocking application network traffic.
    Uses native Windows netsh utility without creating visible console windows.
    """

    RULE_PREFIX = "NetManager_Block_"

    def __init__(self):
        self._blocked_paths: Set[str] = set()
        self.sync_blocked_rules()

    def _normalize_path(self, path: str) -> str:
        """Normalize executable path for consistent comparison."""
        if not path:
            return ""
        return os.path.normcase(os.path.normpath(path.strip()))

    def _generate_rule_id(self, app_name: str, exe_path: str) -> str:
        """Generate a unique, sanitized rule identifier based on path hash."""
        clean_name = re.sub(r'[^a-zA-Z0-9_-]', '_', app_name)[:20]
        path_hash = hashlib.md5(self._normalize_path(exe_path).encode('utf-8')).hexdigest()[:8]
        return f"{self.RULE_PREFIX}{clean_name}_{path_hash}"

    def sync_blocked_rules(self) -> Set[str]:
        """
        Query Windows Firewall for all existing NetManager block rules
        and populate the in-memory cache.
        """
        self._blocked_paths.clear()
        try:
            # Query all rules with NetManager prefix using netsh
            cmd = f'netsh advfirewall firewall show rule name=all'
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                creationflags=CREATE_NO_WINDOW
            )
            
            if result.returncode == 0:
                current_rule_is_ours = False
                for line in result.stdout.splitlines():
                    line = line.strip()
                    if line.startswith("Rule Name:") or line.startswith("Tên quy tắc:"):
                        current_rule_is_ours = self.RULE_PREFIX in line
                    elif current_rule_is_ours and (line.startswith("Program:") or line.startswith("Chương trình:")):
                        parts = line.split(":", 1)
                        if len(parts) > 1:
                            prog_path = parts[1].strip()
                            if prog_path and prog_path.lower() != "any":
                                self._blocked_paths.add(self._normalize_path(prog_path))
                        current_rule_is_ours = False
        except Exception as e:
            print(f"[FirewallService] Error syncing rules: {e}")

        return self._blocked_paths

    def is_blocked(self, exe_path: str) -> bool:
        """Check if an executable is currently in the blocked set."""
        if not exe_path:
            return False
        return self._normalize_path(exe_path) in self._blocked_paths

    def block_application(self, app_name: str, exe_path: str) -> bool:
        """
        Create outbound and inbound block rules for the specified executable.
        """
        if not exe_path or not os.path.exists(exe_path):
            print(f"[FirewallService] Exe path does not exist: {exe_path}")
            return False

        norm_path = self._normalize_path(exe_path)
        rule_id = self._generate_rule_id(app_name, exe_path)

        try:
            # 1. Add Outbound Block Rule
            cmd_out = (
                f'netsh advfirewall firewall add rule '
                f'name="{rule_id}_OUT" dir=out action=block '
                f'program="{exe_path}" enable=yes'
            )
            # 2. Add Inbound Block Rule
            cmd_in = (
                f'netsh advfirewall firewall add rule '
                f'name="{rule_id}_IN" dir=in action=block '
                f'program="{exe_path}" enable=yes'
            )

            res_out = subprocess.run(cmd_out, shell=True, capture_output=True, creationflags=CREATE_NO_WINDOW)
            res_in = subprocess.run(cmd_in, shell=True, capture_output=True, creationflags=CREATE_NO_WINDOW)

            if res_out.returncode == 0 and res_in.returncode == 0:
                self._blocked_paths.add(norm_path)
                return True
            else:
                print(f"[FirewallService] Failed to add rule: {res_out.stderr.decode('utf-8', errors='ignore')}")
                return False
        except Exception as e:
            print(f"[FirewallService] Exception adding firewall rule: {e}")
            return False

    def unblock_application(self, app_name: str, exe_path: str) -> bool:
        """
        Delete outbound and inbound block rules for the specified executable.
        """
        if not exe_path:
            return False

        norm_path = self._normalize_path(exe_path)
        rule_id = self._generate_rule_id(app_name, exe_path)

        try:
            cmd_out = f'netsh advfirewall firewall delete rule name="{rule_id}_OUT"'
            cmd_in = f'netsh advfirewall firewall delete rule name="{rule_id}_IN"'

            subprocess.run(cmd_out, shell=True, capture_output=True, creationflags=CREATE_NO_WINDOW)
            subprocess.run(cmd_in, shell=True, capture_output=True, creationflags=CREATE_NO_WINDOW)

            if norm_path in self._blocked_paths:
                self._blocked_paths.remove(norm_path)
            return True
        except Exception as e:
            print(f"[FirewallService] Exception removing firewall rule: {e}")
            return False

    def get_all_blocked_paths(self) -> Set[str]:
        """Return the current set of blocked executable paths."""
        return set(self._blocked_paths)
