import sys
import os

# Add project root directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QIcon
from PyQt6.QtNetwork import QLocalSocket, QLocalServer

from core.elevation import WindowsElevationService
from core.firewall_service import WindowsFirewallService
from core.process_scanner import WindowsProcessScanner
from controllers.app_controller import AppController
from ui.theme import ThemeManager
from ui.components.splash_screen import SplashScreen
from ui.main_window import MainWindow

SINGLE_INSTANCE_KEY = "Kayzit_NetManager_SingleInstance_Key_v1"


def get_resource_path(relative_path: str) -> str:
    """Get absolute path to resource, works for dev and for PyInstaller bundle."""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), relative_path)


def main():
    # 1. Initialize Qt Application
    app = QApplication(sys.argv)
    app.setApplicationName("Kayzit NetManager")
    app.setOrganizationName("Kayzit")

    # 2. Check for Single Instance via QLocalSocket
    client_socket = QLocalSocket()
    client_socket.connectToServer(SINGLE_INSTANCE_KEY)
    if client_socket.waitForConnected(400):
        # Connected to existing instance! Send activate signal and exit immediately
        client_socket.write(b"ACTIVATE\n")
        client_socket.waitForBytesWritten(400)
        client_socket.disconnectFromServer()
        sys.exit(0)

    # 3. Elevation Service & Check for Primary Instance
    elevation_service = WindowsElevationService()
    is_admin = elevation_service.is_admin()

    if not is_admin and "--no-elevate" not in sys.argv:
        print("[NetManager] Requesting Administrator privileges...")
        elevated = elevation_service.elevate()
        if elevated:
            sys.exit(0)
        else:
            print("[NetManager] Elevation cancelled or failed. Running in Standard mode.")

    # 4. Set Up Single-Instance Server for Primary Instance
    single_server = QLocalServer(app)
    QLocalServer.removeServer(SINGLE_INSTANCE_KEY)
    single_server.listen(SINGLE_INSTANCE_KEY)

    icon_path = get_resource_path(os.path.join("resources", "icon.png"))
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    # Apply Windows 11 Fluent Control Room Dark Theme
    ThemeManager.apply_theme(app, "dark")

    # 5. Fast Splash Screen display
    splash = SplashScreen()
    splash.show()
    app.processEvents()

    splash.set_progress(25, "Verifying security & privileges...")
    app.processEvents()

    # 6. Instantiate Domain Services
    firewall_service = WindowsFirewallService()
    process_scanner = WindowsProcessScanner()

    splash.set_progress(60, "Scanning active network sockets & processes...")
    app.processEvents()

    # 7. Instantiate Main Window (View) & Controller (Presenter)
    window = MainWindow(is_admin=is_admin)
    controller = AppController(
        scanner=process_scanner,
        firewall=firewall_service,
        elevation=elevation_service,
        view=window
    )
    controller.set_view(window)

    # Connect single instance server to activate window
    def _handle_new_instance():
        client = single_server.nextPendingConnection()
        if client:
            client.waitForReadyRead(300)
            window.restore_and_activate()
            client.disconnectFromServer()

    single_server.newConnection.connect(_handle_new_instance)

    splash.set_progress(95, "Ready! Launching Control Room...")
    app.processEvents()

    # 8. Smoothly transition from Splash to Main Window
    def _reveal_main_window():
        splash.close()
        window.show()
        controller.start()

    QTimer.singleShot(350, _reveal_main_window)

    # 9. Run Qt Event Loop
    exit_code = app.exec()

    # Clean up
    single_server.close()
    QLocalServer.removeServer(SINGLE_INSTANCE_KEY)
    controller.stop()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
