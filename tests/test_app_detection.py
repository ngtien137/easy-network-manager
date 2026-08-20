import ctypes
from ctypes import wintypes
import psutil

user32 = ctypes.windll.user32
dwmapi = ctypes.windll.dwmapi

WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)

DWMWA_CLOAKED = 14
WS_EX_TOOLWINDOW = 0x00000080
WS_EX_APPWINDOW = 0x00040000
GW_OWNER = 4

app_pids = set()
app_info = {}

def is_valid_app_window(hwnd):
    if not user32.IsWindowVisible(hwnd):
        return False
        
    length = user32.GetWindowTextLengthW(hwnd)
    if length == 0:
        return False
        
    buf = ctypes.create_unicode_buffer(length + 1)
    user32.GetWindowTextW(hwnd, buf, length + 1)
    title = buf.value.strip()
    if not title:
        return False
        
    # Check cloaked (UWP suspended / hidden virtual desktop)
    cloaked = ctypes.c_int(0)
    try:
        if dwmapi.DwmGetWindowAttribute(hwnd, DWMWA_CLOAKED, ctypes.byref(cloaked), ctypes.sizeof(cloaked)) == 0:
            if cloaked.value != 0:
                return False
    except:
        pass

    # Check window rect
    rect = wintypes.RECT()
    user32.GetWindowRect(hwnd, ctypes.byref(rect))
    w = rect.right - rect.left
    h = rect.bottom - rect.top
    if w <= 30 or h <= 30:
        return False

    # Check styles & owner
    ex_style = user32.GetWindowLongW(hwnd, -20) # GWL_EXSTYLE
    is_tool = bool(ex_style & WS_EX_TOOLWINDOW)
    is_app_win = bool(ex_style & WS_EX_APPWINDOW)
    if is_tool and not is_app_win:
        return False
        
    owner = user32.GetWindow(hwnd, GW_OWNER)
    if owner != 0:
        return False

    # Filter system shell helper titles
    if title in ["Program Manager", "Settings", "Windows Input Experience", "Taskbar", "Start", "Battery Meter", "Network"]:
        return False

    pid = wintypes.DWORD()
    user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
    if pid.value > 4:
        app_pids.add(pid.value)
        app_info[pid.value] = title
        return True
    return False

def enum_cb(hwnd, lparam):
    is_valid_app_window(hwnd)
    return True

hdesk = user32.OpenInputDesktop(0, False, 0x0100)
cb = WNDENUMPROC(enum_cb)
if hdesk:
    user32.EnumDesktopWindows(hdesk, cb, 0)
    user32.CloseDesktop(hdesk)
user32.EnumWindows(cb, 0)

print(f"Detected {len(app_info)} real interactive desktop Apps:")
for pid, title in app_info.items():
    try:
        p = psutil.Process(pid)
        print(f" - [PID {pid:5d}] {p.name():20s} -> '{title}'")
    except Exception:
        pass
