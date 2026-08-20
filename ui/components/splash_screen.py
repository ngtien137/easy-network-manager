import os
import sys
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar, QGraphicsDropShadowEffect
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QPixmap, QColor, QFont

from ui.theme import ThemeManager


def get_resource_path(relative_path: str) -> str:
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    return os.path.join(base_dir, relative_path)


class SplashScreen(QWidget):
    """
    Sleek, fast-loading splash screen with Kayzit brand, progress track, and live status messages.
    """

    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.SplashScreen | Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(460, 260)

        self._setup_ui()

    def _setup_ui(self):
        # Center card container
        card = QWidget(self)
        card.setGeometry(10, 10, 440, 240)
        card.setStyleSheet("""
            QWidget {
                background-color: #11141b;
                border: 1.5px solid #20b8f2;
                border-radius: 14px;
            }
        """)

        # Drop shadow
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(25)
        shadow.setColor(QColor(32, 184, 242, 120))
        shadow.setOffset(0, 4)
        card.setGraphicsEffect(shadow)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(24, 24, 24, 20)
        layout.setSpacing(10)

        # Header with Logo & Brand
        header_layout = QHBoxLayout()
        header_layout.setSpacing(14)

        self.lbl_icon = QLabel()
        icon_path = get_resource_path(os.path.join("resources", "icon.png"))
        if os.path.exists(icon_path):
            pix = QPixmap(icon_path).scaled(48, 48, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.lbl_icon.setPixmap(pix)
        else:
            self.lbl_icon.setText("⚡")
            self.lbl_icon.setStyleSheet("font-size: 32px; color: #20b8f2; border: none;")

        self.lbl_icon.setStyleSheet("border: none; background: transparent;")
        header_layout.addWidget(self.lbl_icon)

        title_box = QVBoxLayout()
        title_box.setSpacing(2)

        lbl_title = QLabel("Kayzit NetManager")
        lbl_title.setStyleSheet("font-size: 20px; font-weight: 800; color: #f2f7fc; border: none; background: transparent; letter-spacing: -0.5px;")

        lbl_sub = QLabel("CONTROL ROOM · FIREWALL ENGINE v1.0.0")
        lbl_sub.setStyleSheet("font-size: 10px; font-weight: 700; color: #20b8f2; border: none; background: transparent; letter-spacing: 1px;")

        title_box.addWidget(lbl_title)
        title_box.addWidget(lbl_sub)
        header_layout.addLayout(title_box, stretch=1)

        layout.addLayout(header_layout)
        layout.addStretch(1)

        # Status Message
        self.lbl_status = QLabel("Initializing security engine...")
        self.lbl_status.setStyleSheet("font-size: 12px; color: #8e99a9; border: none; background: transparent;")
        layout.addWidget(self.lbl_status)

        # Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(15)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(6)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                background-color: rgba(255, 255, 255, 0.06);
                border: none;
                border-radius: 3px;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #20b8f2, stop:1 #41e6a5);
                border-radius: 3px;
            }
        """)
        layout.addWidget(self.progress_bar)

        # Footer copyright
        lbl_footer = QLabel("Copyright © 2026 Kayzit. All rights reserved.")
        lbl_footer.setStyleSheet("font-size: 10px; color: #505c6d; border: none; background: transparent;")
        lbl_footer.setAlignment(Qt.AlignmentFlag.AlignRight)
        layout.addWidget(lbl_footer)

    def set_progress(self, value: int, message: str = ""):
        """Update progress bar and status text smoothly."""
        self.progress_bar.setValue(value)
        if message:
            self.lbl_status.setText(message)
