from PyQt6.QtWidgets import (
    QFrame, QHBoxLayout, QLineEdit, QPushButton, QLabel, QWidget
)
from PyQt6.QtCore import Qt, pyqtSignal
from core.i18n import i18n


class Topbar(QFrame):
    """
    Top Bar Header with global search, language toggle, theme toggle, and admin badge.
    """

    search_changed = pyqtSignal(str)
    theme_toggled = pyqtSignal()
    language_toggled = pyqtSignal(str)

    def __init__(self, is_admin: bool = False, current_theme: str = "dark", parent=None):
        super().__init__(parent)
        self.setObjectName("Topbar")
        self.setFixedHeight(64)
        self.is_admin = is_admin
        self.current_theme = current_theme

        self._setup_ui()
        i18n.language_changed.connect(self.retranslate)

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 10, 20, 10)
        layout.setSpacing(12)

        # Global Search Bar
        self.search_input = QLineEdit()
        self.search_input.setObjectName("GlobalSearch")
        self.search_input.setPlaceholderText(i18n["search"])
        self.search_input.textChanged.connect(self.search_changed.emit)
        layout.addWidget(self.search_input, stretch=1)

        layout.addStretch(1)

        # Language Switch Button
        self.btn_lang = QPushButton(f"{i18n.current_language.upper()} · {'EN' if i18n.current_language=='vi' else 'VI'}")
        self.btn_lang.setObjectName("TopActionBtn")
        self.btn_lang.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_lang.clicked.connect(self._toggle_lang)
        layout.addWidget(self.btn_lang)

        # Theme Switch Button
        self.btn_theme = QPushButton("☀️" if self.current_theme == "dark" else "🌙")
        self.btn_theme.setObjectName("TopActionBtn")
        self.btn_theme.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_theme.clicked.connect(self._on_theme_clicked)
        layout.addWidget(self.btn_theme)

        # Admin Badge
        self.lbl_admin = QLabel(f"🛡️ {i18n['admin']}")
        self.lbl_admin.setObjectName("AdminChip")
        if not self.is_admin:
            self.lbl_admin.setText("⚠️ Standard")
            self.lbl_admin.setStyleSheet("background-color: rgba(251, 191, 36, 0.1); color: #fbbf24; border: 1px solid rgba(251, 191, 36, 0.3); border-radius: 6px; padding: 4px 8px; font-size: 11px; font-weight: 700;")
        layout.addWidget(self.lbl_admin)

    def _toggle_lang(self):
        new_lang = "en" if i18n.current_language == "vi" else "vi"
        i18n.set_language(new_lang)
        self.language_toggled.emit(new_lang)

    def _on_theme_clicked(self):
        self.current_theme = "light" if self.current_theme == "dark" else "dark"
        self.btn_theme.setText("☀️" if self.current_theme == "dark" else "🌙")
        self.theme_toggled.emit()

    def retranslate(self):
        self.search_input.setPlaceholderText(i18n["search"])
        self.btn_lang.setText(f"{i18n.current_language.upper()} · {'EN' if i18n.current_language=='vi' else 'VI'}")
        if self.is_admin:
            self.lbl_admin.setText(f"🛡️ {i18n['admin']}")
