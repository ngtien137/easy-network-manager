import sys
import os
import ctypes
from .interfaces import IElevationService


class WindowsElevationService(IElevationService):
    """
    Handles checking and elevating Windows Administrator permissions.
    """

    def is_admin(self) -> bool:
        """Check whether the current script is running with elevated UAC permissions."""
        try:
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except Exception:
            return False

    def elevate(self) -> bool:
        """
        Relaunch the current script with elevated privileges using ShellExecuteW ('runas').
        Ensures absolute script path and current working directory are preserved.
        """
        if self.is_admin():
            return True

        try:
            # Reconstruct arguments with absolute path for script
            script_path = os.path.abspath(sys.argv[0])
            work_dir = os.path.dirname(script_path)
            
            # Additional args (skip sys.argv[0])
            extra_args = sys.argv[1:]
            params = f'"{script_path}" ' + " ".join([f'"{arg}"' for arg in extra_args])

            ret = ctypes.windll.shell32.ShellExecuteW(
                None,
                "runas",
                sys.executable,
                params.strip(),
                work_dir,
                1  # SW_SHOWNORMAL
            )
            # ShellExecute returns > 32 on success
            return ret > 32
        except Exception as e:
            print(f"[ElevationService] Failed to elevate: {e}")
            return False
