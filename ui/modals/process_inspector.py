from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QWidget
)
from PyQt6.QtCore import Qt, pyqtSignal
from core.models import ProcessItem, NetworkState
from core.i18n import i18n
from ui.components.status_badge import StatusBadge


class ProcessInspectorModal(QDialog):
    """
    Process Inspector Modal Dialog matching the exact design in the Web Demo.
    """

    block_requested = pyqtSignal(object)
    unblock_requested = pyqtSignal(object)
    view_traffic_requested = pyqtSignal(object)

    def __init__(self, process: ProcessItem, parent=None):
        super().__init__(parent)
        self.process = process
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(480, 420)

        self._setup_ui()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # Card container
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #202630, stop:1 #15181e);
                border: 1px solid rgba(172, 218, 236, 0.22);
                border-radius: 14px;
            }
        """)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(24, 20, 24, 22)
        card_layout.setSpacing(14)

        # Top Row (Close button)
        top_row = QHBoxLayout()
        lbl_eyebrow = QLabel(i18n["inspector"])
        lbl_eyebrow.setObjectName("Eyebrow")
        lbl_eyebrow.setStyleSheet("color: #7790a6; font-size: 10px; font-weight: 700; letter-spacing: 1.2px;")

        btn_close = QPushButton("✕")
        btn_close.setFixedSize(28, 28)
        btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_close.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #9aaabb;
                border: none;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                color: #ffffff;
                background: rgba(255, 255, 255, 0.08);
                border-radius: 4px;
            }
        """)
        btn_close.clicked.connect(self.close)

        top_row.addWidget(lbl_eyebrow)
        top_row.addStretch(1)
        top_row.addWidget(btn_close)
        card_layout.addLayout(top_row)

        # Header Info (Avatar + Name + PID)
        header_row = QHBoxLayout()
        header_row.setSpacing(14)

        lbl_avatar = QLabel(self.process.icon_text or "AP")
        lbl_avatar.setFixedSize(44, 44)
        lbl_avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_avatar.setStyleSheet("""
            background: #222834;
            color: #c8d8e8;
            border: 1px solid rgba(255, 255, 255, 0.15);
            border-radius: 11px;
            font-size: 13px;
            font-weight: 700;
        """)

        title_box = QVBoxLayout()
        title_box.setSpacing(2)
        lbl_name = QLabel(self.process.display_name)
        lbl_name.setStyleSheet("font-size: 20px; font-weight: 700; color: #f2f7fc;")
        lbl_sub = QLabel(f"{self.process.name} · PID {self.process.pid}")
        lbl_sub.setStyleSheet("font-size: 12px; color: #8e99a9;")
        title_box.addWidget(lbl_name)
        title_box.addWidget(lbl_sub)

        header_row.addWidget(lbl_avatar)
        header_row.addLayout(title_box, stretch=1)
        card_layout.addLayout(header_row)

        # State Row
        state_box = QFrame()
        state_box.setStyleSheet("background: rgba(255, 255, 255, 0.035); border: 1px solid rgba(213, 225, 240, 0.10); border-radius: 8px; padding: 6px 12px;")
        state_layout = QHBoxLayout(state_box)
        lbl_state_title = QLabel(i18n["currentState"])
        lbl_state_title.setStyleSheet("color: #8e99a9; font-size: 12px;")
        badge = StatusBadge(self.process.network_state)
        state_layout.addWidget(lbl_state_title)
        state_layout.addStretch(1)
        state_layout.addWidget(badge)
        card_layout.addWidget(state_box)

        # Details Table
        details_box = QFrame()
        details_box.setStyleSheet("background: rgba(0, 0, 0, 0.2); border: 1px solid rgba(213, 225, 240, 0.10); border-radius: 8px;")
        dt_layout = QVBoxLayout(details_box)
        dt_layout.setContentsMargins(12, 10, 12, 10)
        dt_layout.setSpacing(10)

        # Path
        dt_layout.addWidget(self._create_detail_row(i18n["processPath"], self.process.exe_path or "N/A"))
        # Connections
        dt_layout.addWidget(self._create_detail_row(i18n["connections"], f"{self.process.connections_count} active socket(s)"))
        # Rule
        rule_desc = "Outbound block rule active" if self.process.network_state == NetworkState.BLOCKED else "No outbound restriction"
        dt_layout.addWidget(self._create_detail_row(i18n["networkRules"], rule_desc))

        card_layout.addWidget(details_box)

        # Action Buttons
        act_row = QHBoxLayout()
        act_row.setSpacing(10)

        btn_view_traffic = QPushButton(f"👁️ {i18n['viewConnection']}")
        btn_view_traffic.setObjectName("QuietBtn")
        btn_view_traffic.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_view_traffic.setFixedHeight(36)
        btn_view_traffic.clicked.connect(self._on_view_traffic)

        act_row.addWidget(btn_view_traffic)
        act_row.addStretch(1)

        if not self.process.is_system and self.process.exe_path:
            is_blocked = self.process.network_state == NetworkState.BLOCKED
            btn_toggle = QPushButton(f"🔓 {i18n['unblock']}" if is_blocked else f"🚫 {i18n['block']}")
            btn_toggle.setObjectName("PrimaryActionBtn")
            btn_toggle.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_toggle.setFixedHeight(36)
            btn_toggle.clicked.connect(self._on_toggle)
            act_row.addWidget(btn_toggle)

        card_layout.addLayout(act_row)
        main_layout.addWidget(card)

    def _create_detail_row(self, label: str, value: str) -> QWidget:
        container = QWidget()
        l = QVBoxLayout(container)
        l.setContentsMargins(0, 0, 0, 0)
        l.setSpacing(2)
        lbl_t = QLabel(label)
        lbl_t.setStyleSheet("color: #778699; font-size: 10px; font-weight: 700; text-transform: uppercase;")
        lbl_v = QLabel(value)
        lbl_v.setStyleSheet("color: #cbd6e2; font-size: 11px;")
        lbl_v.setWordWrap(True)
        l.addWidget(lbl_t)
        l.addWidget(lbl_v)
        return container

    def _on_toggle(self):
        if self.process.network_state == NetworkState.BLOCKED:
            self.unblock_requested.emit(self.process)
        else:
            self.block_requested.emit(self.process)
        self.accept()

    def _on_view_traffic(self):
        self.view_traffic_requested.emit(self.process)
        self.accept()
