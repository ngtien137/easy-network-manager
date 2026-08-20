import os
import time
import psutil
import ctypes
from ctypes import wintypes
from typing import List, Dict, Set, Optional
from collections import defaultdict

from .models import ProcessItem, ProcessCategory, NetworkState, SystemResourceSummary, SocketConnection
from .interfaces import IProcessScanner

user32 = ctypes.windll.user32
dwmapi = ctypes.windll.dwmapi

WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)

DWMWA_CLOAKED = 14
WS_EX_TOOLWINDOW = 0x00000080
WS_EX_APPWINDOW = 0x00040000
GW_OWNER = 4

SYSTEM_EXECUTABLES = {
    "system", "registry", "smss.exe", "csrss.exe", "wininit.exe",
    "services.exe", "lsass.exe", "svchost.exe", "fontdrvhost.exe",
    "dwm.exe", "memory compression", "msmpeng.exe", "nissrv.exe",
    "spoolsv.exe", "searchindexer.exe", "sihost.exe", "taskhostw.exe"
}

KNOWN_APP_NAMES = {
    "chrome.exe": "Google Chrome",
    "msedge.exe": "Microsoft Edge",
    "firefox.exe": "Mozilla Firefox",
    "code.exe": "Visual Studio Code",
    "discord.exe": "Discord",
    "spotify.exe": "Spotify",
    "telegram.exe": "Telegram Desktop",
    "windowsterminal.exe": "Windows Terminal",
    "notepad.exe": "Notepad",
    "taskmgr.exe": "Task Manager",
    "explorer.exe": "Windows Explorer",
    "steam.exe": "Steam",
    "steamwebhelper.exe": "Steam Web Helper",
    "devenv.exe": "Visual Studio",
    "slack.exe": "Slack",
    "vlc.exe": "VLC Media Player",
    "obs64.exe": "OBS Studio"
}


class WindowsProcessScanner(IProcessScanner):
    """
    Scans and categorizes Windows processes matching Windows Task Manager logic.
    Identifies interactive Apps via top-level taskbar/desktop window enumeration (OpenInputDesktop),
    groups child processes under root app, and identifies system background services.
    """

    def __init__(self):
        # Initialize CPU percent & Network I/O baselines
        psutil.cpu_percent(interval=None)
        self._last_net_io = psutil.net_io_counters()
        self._last_net_time = time.time()

    def _get_interactive_app_pids(self) -> Set[int]:
        """
        Enumerate all top-level taskbar/desktop visible windows using Windows Task Manager's
        window filtering rules to determine which PIDs are interactive Apps.
        """
        app_pids: Set[int] = set()

        def enum_callback(hwnd, lparam):
            try:
                # 1. Must be visible
                if not user32.IsWindowVisible(hwnd):
                    return True

                # 2. Must have a title
                length = user32.GetWindowTextLengthW(hwnd)
                if length == 0:
                    return True

                buf = ctypes.create_unicode_buffer(length + 1)
                user32.GetWindowTextW(hwnd, buf, length + 1)
                title = buf.value.strip()
                if not title:
                    return True

                # 3. Must not be cloaked (minimized UWP or hidden virtual desktop)
                cloaked = ctypes.c_int(0)
                try:
                    if dwmapi.DwmGetWindowAttribute(hwnd, DWMWA_CLOAKED, ctypes.byref(cloaked), ctypes.sizeof(cloaked)) == 0:
                        if cloaked.value != 0:
                            return True
                except Exception:
                    pass

                # 4. Must have non-zero dimensions
                rect = wintypes.RECT()
                user32.GetWindowRect(hwnd, ctypes.byref(rect))
                w = rect.right - rect.left
                h = rect.bottom - rect.top
                if w <= 30 or h <= 30:
                    return True

                # 5. Check styles & Owner (Must not be pure tool window)
                ex_style = user32.GetWindowLongW(hwnd, -20)
                is_tool = bool(ex_style & WS_EX_TOOLWINDOW)
                is_app_win = bool(ex_style & WS_EX_APPWINDOW)
                if is_tool and not is_app_win:
                    return True

                owner = user32.GetWindow(hwnd, GW_OWNER)
                if owner != 0:
                    return True

                # 6. Filter system shell background windows
                if title in ["Program Manager", "Settings", "Windows Input Experience", "Taskbar", "Start", "Battery Meter", "Network"]:
                    return True

                pid = wintypes.DWORD()
                user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
                if pid.value > 4:
                    app_pids.add(pid.value)

            except Exception:
                pass
            return True

        cb = WNDENUMPROC(enum_callback)
        # Open interactive input desktop
        hdesk = user32.OpenInputDesktop(0, False, 0x0100)
        if hdesk:
            user32.EnumDesktopWindows(hdesk, cb, 0)
            user32.CloseDesktop(hdesk)
        user32.EnumWindows(cb, 0)

        return app_pids

    def _get_avatar_text(self, name: str) -> str:
        """Extract 2-letter uppercase initials for avatar badge."""
        clean = name.replace(".exe", "").strip()
        words = clean.split()
        if len(words) >= 2:
            return f"{words[0][0]}{words[1][0]}".upper()
        return clean[:2].upper()

    def scan_all(self, blocked_paths: Set[str]) -> List[ProcessItem]:
        """
        Scan all active processes, categorize into Apps / Background,
        aggregate instances (e.g. Chrome tabs), and check firewall block state.
        """
        app_pids = self._get_interactive_app_pids()
        grouped_apps: Dict[str, Dict] = defaultdict(lambda: {
            'pids': [],
            'name': '',
            'display_name': '',
            'exe': '',
            'category': ProcessCategory.BACKGROUND,
            'cpu': 0.0,
            'memory_bytes': 0,
            'username': '',
            'status': 'running',
            'is_system': False,
            'connections_count': 0
        })

        for proc in psutil.process_iter(['pid', 'name', 'exe', 'cpu_percent', 'memory_info', 'username', 'status']):
            try:
                info = proc.info
                pid = info['pid']
                name = info['name'] or f"Process_{pid}"
                exe = info['exe'] or ""
                mem_info = info['memory_info']
                mem_bytes = mem_info.rss if mem_info else 0
                cpu = info['cpu_percent'] or 0.0
                username = info['username'] or ""
                status = info['status'] or "running"

                name_lower = name.lower()
                is_app = pid in app_pids
                is_system = name_lower in SYSTEM_EXECUTABLES or (username and "system" in username.lower() and not is_app)

                group_key = exe.lower() if exe else f"name_{name_lower}"

                data = grouped_apps[group_key]
                data['pids'].append(pid)
                data['name'] = name
                
                # Friendly display name
                if name_lower in KNOWN_APP_NAMES:
                    data['display_name'] = KNOWN_APP_NAMES[name_lower]
                else:
                    data['display_name'] = name.replace(".exe", "")

                if exe:
                    data['exe'] = exe
                data['cpu'] += cpu
                data['memory_bytes'] += mem_bytes
                if username and not data['username']:
                    data['username'] = username
                data['status'] = status
                
                # If ANY process under this executable has an interactive GUI window, classify the whole app as APP
                if is_app:
                    data['category'] = ProcessCategory.APP
                if is_system:
                    data['is_system'] = True

            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
            except Exception:
                continue

        # Count active connections per process
        try:
            for conn in psutil.net_connections(kind='inet'):
                if conn.pid:
                    for g in grouped_apps.values():
                        if conn.pid in g['pids']:
                            g['connections_count'] += 1
        except Exception:
            pass

        items: List[ProcessItem] = []
        for group_key, data in grouped_apps.items():
            count = len(data['pids'])
            main_pid = data['pids'][0]
            exe_path = data['exe']
            display_name = data['display_name']

            norm_exe = os.path.normcase(os.path.normpath(exe_path)) if exe_path else ""
            is_blocked = norm_exe in blocked_paths if norm_exe else False

            if data['is_system']:
                net_state = NetworkState.SYSTEM
            elif is_blocked:
                net_state = NetworkState.BLOCKED
            else:
                net_state = NetworkState.ALLOWED

            # Estimated speed string
            if net_state == NetworkState.BLOCKED:
                speed_str = "0 KB/s"
            elif data['connections_count'] > 0:
                speed_str = f"{data['connections_count'] * 12} KB/s"
            else:
                speed_str = "0 KB/s"

            item = ProcessItem(
                pid=main_pid,
                name=data['name'],
                display_name=display_name,
                exe_path=exe_path,
                category=data['category'],
                cpu_percent=round(data['cpu'], 1),
                memory_bytes=data['memory_bytes'],
                network_state=net_state,
                network_speed=speed_str,
                connections_count=data['connections_count'],
                instance_count=count,
                child_pids=data['pids'],
                username=data['username'],
                status=data['status'],
                is_system=data['is_system'],
                icon_text=self._get_avatar_text(display_name)
            )
            items.append(item)

        # Sort: Apps first, then by Memory descending
        items.sort(key=lambda x: (x.category != ProcessCategory.APP, -x.memory_bytes))
        return items

    def get_system_summary(self, processes: List[ProcessItem]) -> SystemResourceSummary:
        """Calculate overall CPU, RAM, Network I/O delta, and counts."""
        try:
            total_cpu = psutil.cpu_percent(interval=None)
            mem = psutil.virtual_memory()
            used_gb = mem.used / (1024 ** 3)
            total_gb = mem.total / (1024 ** 3)
            mem_pct = mem.percent

            # Measure real Network I/O rate
            now = time.time()
            dt = max(now - self._last_net_time, 0.1)
            current_io = psutil.net_io_counters()
            dl_bytes_sec = max(current_io.bytes_recv - self._last_net_io.bytes_recv, 0) / dt
            ul_bytes_sec = max(current_io.bytes_sent - self._last_net_io.bytes_sent, 0) / dt
            self._last_net_io = current_io
            self._last_net_time = now

            def fmt_speed(bps: float) -> str:
                if bps >= 1024 * 1024:
                    return f"{bps / (1024*1024):.1f} MB/s"
                elif bps >= 1024:
                    return f"{bps / 1024:.0f} KB/s"
                return f"{bps:.0f} B/s"

            apps_count = sum(1 for p in processes if p.category == ProcessCategory.APP)
            bg_count = sum(1 for p in processes if p.category == ProcessCategory.BACKGROUND)
            blocked_count = sum(1 for p in processes if p.network_state == NetworkState.BLOCKED)
            total_conns = sum(p.connections_count for p in processes)

            return SystemResourceSummary(
                total_cpu_percent=round(total_cpu, 1),
                total_memory_percent=round(mem_pct, 1),
                used_memory_gb=round(used_gb, 1),
                total_memory_gb=round(total_gb, 1),
                download_speed=fmt_speed(dl_bytes_sec),
                upload_speed=fmt_speed(ul_bytes_sec),
                download_bytes_sec=dl_bytes_sec,
                upload_bytes_sec=ul_bytes_sec,
                total_apps_count=apps_count,
                total_background_count=bg_count,
                total_blocked_count=blocked_count,
                total_connections_count=total_conns
            )
        except Exception:
            return SystemResourceSummary()

    def get_active_sockets(self, blocked_paths: Set[str]) -> List[SocketConnection]:
        """Fetch active TCP/UDP socket connections."""
        sockets: List[SocketConnection] = []
        try:
            pids_to_name = {p.pid: p.name() for p in psutil.process_iter(['pid', 'name'])}
            pids_to_exe = {p.pid: p.exe() for p in psutil.process_iter(['pid', 'exe'])}

            for i, conn in enumerate(psutil.net_connections(kind='inet')[:40]):
                if not conn.laddr:
                    continue
                local = f"{conn.laddr.ip}:{conn.laddr.port}"
                remote = f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else "*:*"
                p_name = pids_to_name.get(conn.pid, "system") if conn.pid else "system"
                exe = pids_to_exe.get(conn.pid, "") if conn.pid else ""

                proto = "TCP" if conn.type == psutil.SOCK_STREAM else "UDP"
                is_blocked = os.path.normcase(os.path.normpath(exe)) in blocked_paths if exe else False

                sockets.append(SocketConnection(
                    id=f"sock_{i}_{conn.pid}",
                    pid=conn.pid or 0,
                    process_name=p_name,
                    local_address=local,
                    remote_address=remote,
                    protocol=f"{proto}/{conn.status if conn.status else 'UDP'}",
                    state=conn.status if conn.status else "OPEN",
                    is_blocked=is_blocked
                ))
        except Exception:
            pass
        return sockets

    def terminate_process(self, pid: int) -> bool:
        """Terminate a process and its children cleanly."""
        try:
            parent = psutil.Process(pid)
            children = parent.children(recursive=True)
            for child in children:
                try:
                    child.terminate()
                except Exception:
                    pass
            parent.terminate()
            return True
        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            print(f"[ProcessScanner] Failed to terminate PID {pid}: {e}")
            return False
