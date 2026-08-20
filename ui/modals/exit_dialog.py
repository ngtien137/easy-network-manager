from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QProgressBar
from PyQt6.QtCore import Qt
from core.i18n import i18n


class ExitCleanupDialog(QDialog):
    """
    Non-blocking feedback dialog shown when restoring firewall rules during application exit.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(380, 160)

        self._setup_ui()

    def _setup_ui(self):
        container = self
        layout = QVBoxLayout(container)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        self.setStyleSheet("""
            QDialog {
                background-color: #13161f;
                border: 1.5px solid #20b8f2;
                border-radius: 12px;
            }
        """)

        lbl_title = QLabel("⚡ Kayzit NetManager")
        lbl_title.setStyleSheet("font-size: 15px; font-weight: 700; color: #f2f7fc;")
        layout.addWidget(lbl_title)

        self.lbl_msg = QLabel("Restoring application network rules before exit...")
        self.lbl_msg.setStyleSheet("font-size: 12px; color: #8e99a9;")
        self.lbl_msg.setWordWrap(True)
        layout.addWidget(self.lbl_msg)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Indeterminate pulsing progress
        self.progress_bar.setFixedHeight(5)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                background-color: rgba(255, 255, 255, 0.08);
                border: none;
                border-radius: 2px;
            }
            QProgressBar::chunk {
                background-color: #20b8f2;
                border-radius: 2px;
            }
        """)
        layout.addWidget(self.progress_bar)
