from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal
from core.i18n import i18n


class ProfileCard(QFrame):
    """Individual Profile Preset Card."""

    apply_clicked = pyqtSignal(str)

    def __init__(self, title_key: str, desc_key: str, rules_count: str, icon_str: str, tone_color: str, parent=None):
        super().__init__(parent)
        self.setObjectName("ProfileCard")
        self.title_key = title_key
        self.desc_key = desc_key
        self.rules_count = rules_count
        self.tone_color = tone_color

        self._setup_ui(icon_str)

    def _setup_ui(self, icon_str: str):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(16)

        # Icon box
        lbl_icon = QLabel(icon_str)
        lbl_icon.setFixedSize(44, 44)
        lbl_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_icon.setStyleSheet(f"""
            background: {self.tone_color}18;
            color: {self.tone_color};
            border: 1px solid {self.tone_color}40;
            border-radius: 11px;
            font-size: 20px;
        """)
        layout.addWidget(lbl_icon)

        # Content Box (Title + Description)
        body = QVBoxLayout()
        body.setSpacing(4)
        self.lbl_title = QLabel(i18n[self.title_key])
        self.lbl_title.setStyleSheet("font-size: 16px; font-weight: 700; color: #f2f7fc;")
        self.lbl_desc = QLabel(i18n[self.desc_key])
        self.lbl_desc.setStyleSheet("font-size: 12px; color: #8e99a9; line-height: 1.4;")
        self.lbl_desc.setWordWrap(True)

        body.addWidget(self.lbl_title)
        body.addWidget(self.lbl_desc)
        layout.addLayout(body, stretch=1)

        # Rule Count Badge
        lbl_rules = QLabel(f"{self.rules_count} rules")
        lbl_rules.setStyleSheet("""
            background: rgba(0, 0, 0, 0.25);
            color: #c7d3df;
            border: 1px solid rgba(213, 225, 240, 0.10);
            border-radius: 6px;
            padding: 6px 12px;
            font-size: 12px;
            font-weight: 700;
        """)
        layout.addWidget(lbl_rules)

        # Apply Button
        self.btn_apply = QPushButton(f"{i18n['apply']}  ▶")
        self.btn_apply.setObjectName("PrimaryActionBtn")
        self.btn_apply.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_apply.setFixedHeight(36)
        self.btn_apply.clicked.connect(lambda: self.apply_clicked.emit(self.title_key))
        layout.addWidget(self.btn_apply)

    def retranslate(self):
        self.lbl_title.setText(i18n[self.title_key])
        self.lbl_desc.setText(i18n[self.desc_key])
        self.btn_apply.setText(f"{i18n['apply']}  ▶")


class ProfilesView(QWidget):
    """
    Smart Firewall Profiles View matching Fluent Control Room.
    """

    profile_applied = pyqtSignal(str)  # 'Gaming mode', 'Focus mode', 'Strict privacy'

    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_profile = "Balanced protection"
        self._setup_ui()
        i18n.language_changed.connect(self.retranslate)

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(28, 24, 28, 20)
        main_layout.setSpacing(16)

        # 1. Page Heading
        heading_layout = QVBoxLayout()
        heading_layout.setSpacing(4)

        self.lbl_eyebrow = QLabel("POLICY STATIONS")
        self.lbl_eyebrow.setObjectName("Eyebrow")

        self.lbl_title = QLabel(i18n["profilesTitle"])
        self.lbl_title.setObjectName("PageTitle")

        self.lbl_sub = QLabel(i18n["profilesSub"])
        self.lbl_sub.setObjectName("PageSubtitle")

        heading_layout.addWidget(self.lbl_eyebrow)
        heading_layout.addWidget(self.lbl_title)
        heading_layout.addWidget(self.lbl_sub)
        main_layout.addLayout(heading_layout)

        # 2. Active Profile Highlight Card
        self.highlight_card = QFrame()
        self.highlight_card.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 rgba(32,184,242,0.18), stop:0.5 rgba(23,26,33,0.85), stop:1 rgba(23,26,33,0.75));
                border: 1px solid rgba(32, 184, 242, 0.28);
                border-radius: 12px;
                padding: 16px 20px;
            }
        """)
        hl_layout = QHBoxLayout(self.highlight_card)
        hl_info = QVBoxLayout()
        hl_info.setSpacing(4)

        self.lbl_hl_tag = QLabel(i18n["activeProfile"])
        self.lbl_hl_tag.setStyleSheet("color: #7adcf9; font-size: 10px; font-weight: 700; letter-spacing: 1px;")

        self.lbl_hl_profile_name = QLabel(self._current_profile)
        self.lbl_hl_profile_name.setStyleSheet("font-size: 24px; font-weight: 700; color: #f2f7fc;")

        self.lbl_hl_status = QLabel("🛡️ Active firewall policy enforcing network security rules.")
        self.lbl_hl_status.setStyleSheet("color: #a4b8c7; font-size: 12px;")

        hl_info.addWidget(self.lbl_hl_tag)
        hl_info.addWidget(self.lbl_hl_profile_name)
        hl_info.addWidget(self.lbl_hl_status)
        hl_layout.addLayout(hl_info, stretch=1)

        lbl_badge_active = QLabel(f"⚡ {i18n['policyActive']}")
        lbl_badge_active.setStyleSheet("""
            background: rgba(32, 184, 242, 0.15);
            color: #aef0ff;
            border: 1px solid rgba(32, 184, 242, 0.35);
            border-radius: 6px;
            padding: 6px 12px;
            font-size: 10px;
            font-weight: 700;
        """)
        hl_layout.addWidget(lbl_badge_active)
        main_layout.addWidget(self.highlight_card)

        # 3. Profile Stack Cards
        self.card_gaming = ProfileCard("gaming", "gamingDesc", "8", "🎮", "#20b8f2")
        self.card_gaming.apply_clicked.connect(lambda: self._apply("Gaming mode"))

        self.card_focus = ProfileCard("focus", "focusDesc", "12", "💼", "#bdc8d4")
        self.card_focus.apply_clicked.connect(lambda: self._apply("Focus mode"))

        self.card_strict = ProfileCard("strict", "strictDesc", "24", "🛡️", "#ff6868")
        self.card_strict.apply_clicked.connect(lambda: self._apply("Strict privacy"))

        main_layout.addWidget(self.card_gaming)
        main_layout.addWidget(self.card_focus)
        main_layout.addWidget(self.card_strict)

        main_layout.addStretch(1)

    def _apply(self, profile_name: str):
        self._current_profile = profile_name
        self.lbl_hl_profile_name.setText(profile_name)
        self.profile_applied.emit(profile_name)

    def set_active_profile(self, profile_name: str, blocked_count: int = 0):
        self._current_profile = profile_name
        self.lbl_hl_profile_name.setText(profile_name)
        self.lbl_hl_status.setText(f"🛡️ {blocked_count} rules are currently enforcing firewall policies.")

    def retranslate(self):
        self.lbl_title.setText(i18n["profilesTitle"])
        self.lbl_sub.setText(i18n["profilesSub"])
        self.lbl_hl_tag.setText(i18n["activeProfile"])
        self.card_gaming.retranslate()
        self.card_focus.retranslate()
        self.card_strict.retranslate()
