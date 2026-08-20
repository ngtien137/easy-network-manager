from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QGridLayout, QCheckBox, QFileDialog, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal, QSettings
from core.i18n import i18n


class SettingCardFrame(QFrame):
    """Container card for a setting section."""
    def __init__(self, title_key: str, desc_key: str, parent=None):
        super().__init__(parent)
        self.setObjectName("SettingCard")
        self.title_key = title_key
        self.desc_key = desc_key

        self.card_layout = QVBoxLayout(self)
        self.card_layout.setContentsMargins(18, 16, 18, 16)
        self.card_layout.setSpacing(12)

        self.lbl_title = QLabel(i18n[title_key])
        self.lbl_title.setStyleSheet("font-size: 15px; font-weight: 700; color: #f2f7fc;")
        self.lbl_desc = QLabel(i18n[desc_key])
        self.lbl_desc.setStyleSheet("font-size: 11px; color: #8e99a9;")

        self.card_layout.addWidget(self.lbl_title)
        self.card_layout.addWidget(self.lbl_desc)

    def add_widget(self, widget: QWidget):
        self.card_layout.addWidget(widget)

    def retranslate(self):
        self.lbl_title.setText(i18n[self.title_key])
        self.lbl_desc.setText(i18n[self.desc_key])


class SettingsView(QWidget):
    """
    Settings & Preferences View matching Fluent Control Room layout.
    """

    language_changed = pyqtSignal(str)
    theme_changed = pyqtSignal(str)
    export_rules_requested = pyqtSignal()
    import_rules_requested = pyqtSignal()
    reset_defaults_requested = pyqtSignal()

    def __init__(self, current_theme: str = "dark", parent=None):
        super().__init__(parent)
        self.current_theme = current_theme
        self.settings = QSettings("NetManagerApp", "NetManager")

        self._setup_ui()
        i18n.language_changed.connect(self.retranslate)

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(28, 24, 28, 20)
        main_layout.setSpacing(16)

        # 1. Page Heading
        heading_layout = QVBoxLayout()
        heading_layout.setSpacing(4)

        self.lbl_eyebrow = QLabel("PREFERENCES")
        self.lbl_eyebrow.setObjectName("Eyebrow")

        self.lbl_title = QLabel(i18n["settingsTitle"])
        self.lbl_title.setObjectName("PageTitle")

        self.lbl_sub = QLabel(i18n["settingsSub"])
        self.lbl_sub.setObjectName("PageSubtitle")

        heading_layout.addWidget(self.lbl_eyebrow)
        heading_layout.addWidget(self.lbl_title)
        heading_layout.addWidget(self.lbl_sub)
        main_layout.addLayout(heading_layout)

        # 2. 2-Column Settings Grid
        grid = QGridLayout()
        grid.setSpacing(14)

        # Card 1: Language
        self.card_lang = SettingCardFrame("language", "languageDesc")
        lang_btn_box = QHBoxLayout()
        lang_btn_box.setSpacing(8)

        self.btn_lang_vi = QPushButton("🇻🇳  VI  Tiếng Việt")
        self.btn_lang_vi.setFixedHeight(38)
        self.btn_lang_vi.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_lang_vi.clicked.connect(lambda: self._set_lang("vi"))

        self.btn_lang_en = QPushButton("🇬🇧  EN  English")
        self.btn_lang_en.setFixedHeight(38)
        self.btn_lang_en.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_lang_en.clicked.connect(lambda: self._set_lang("en"))

        lang_btn_box.addWidget(self.btn_lang_vi)
        lang_btn_box.addWidget(self.btn_lang_en)
        self.card_lang.card_layout.addLayout(lang_btn_box)
        grid.addWidget(self.card_lang, 0, 0)

        # Card 2: Appearance
        self.card_theme = SettingCardFrame("appearance", "appearance")
        theme_btn_box = QHBoxLayout()
        theme_btn_box.setSpacing(8)

        self.btn_theme_dark = QPushButton(f"🌙  {i18n['dark']}")
        self.btn_theme_dark.setFixedHeight(38)
        self.btn_theme_dark.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_theme_dark.clicked.connect(lambda: self._set_theme("dark"))

        self.btn_theme_light = QPushButton(f"☀️  {i18n['light']}")
        self.btn_theme_light.setFixedHeight(38)
        self.btn_theme_light.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_theme_light.clicked.connect(lambda: self._set_theme("light"))

        theme_btn_box.addWidget(self.btn_theme_dark)
        theme_btn_box.addWidget(self.btn_theme_light)
        self.card_theme.card_layout.addLayout(theme_btn_box)
        grid.addWidget(self.card_theme, 0, 1)

        # Card 3: Firewall Behavior
        self.card_fw = SettingCardFrame("firewall", "firewall")
        self.chk_auto_uac = QCheckBox(i18n["autoUac"])
        self.chk_auto_uac.setChecked(True)
        self.chk_notify = QCheckBox(i18n["notify"])
        self.chk_notify.setChecked(self.settings.value("notify_new_conns", False, type=bool))
        self.chk_notify.toggled.connect(lambda c: self.settings.setValue("notify_new_conns", c))

        self.card_fw.card_layout.addWidget(self.chk_auto_uac)
        self.card_fw.card_layout.addWidget(self.chk_notify)
        grid.addWidget(self.card_fw, 1, 0)

        # Card 4: Startup & System Tray
        self.card_startup = SettingCardFrame("startup", "startup")
        self.chk_startup = QCheckBox(i18n["startWindows"])
        self.chk_startup.setChecked(self.settings.value("run_on_startup", False, type=bool))
        self.chk_startup.toggled.connect(lambda c: self.settings.setValue("run_on_startup", c))

        self.chk_tray = QCheckBox(i18n["tray"])
        self.chk_tray.setChecked(self.settings.value("minimize_to_tray", True, type=bool))
        self.chk_tray.toggled.connect(lambda c: self.settings.setValue("minimize_to_tray", c))

        self.card_startup.card_layout.addWidget(self.chk_startup)
        self.card_startup.card_layout.addWidget(self.chk_tray)
        grid.addWidget(self.card_startup, 1, 1)

        # Card 5: Data & Rules
        self.card_data = SettingCardFrame("dataRules", "dataRules")
        data_act_box = QHBoxLayout()
        data_act_box.setSpacing(8)

        btn_export = QPushButton(f"📥  {i18n['export']}")
        btn_export.setObjectName("QuietBtn")
        btn_export.setFixedHeight(34)
        btn_export.clicked.connect(self.export_rules_requested.emit)

        btn_import = QPushButton(f"📤  {i18n['import']}")
        btn_import.setObjectName("QuietBtn")
        btn_import.setFixedHeight(34)
        btn_import.clicked.connect(self.import_rules_requested.emit)

        btn_reset = QPushButton(f"⚠️  {i18n['reset']}")
        btn_reset.setObjectName("QuietBtn")
        btn_reset.setStyleSheet("color: #ff9f9f; border-color: rgba(255,104,104,0.3);")
        btn_reset.setFixedHeight(34)
        btn_reset.clicked.connect(self.reset_defaults_requested.emit)

        data_act_box.addWidget(btn_export)
        data_act_box.addWidget(btn_import)
        data_act_box.addWidget(btn_reset)
        self.card_data.card_layout.addLayout(data_act_box)
        grid.addWidget(self.card_data, 2, 0, 1, 2)

        main_layout.addLayout(grid)
        main_layout.addStretch(1)

        self._update_selection_buttons()

    def _set_lang(self, lang: str):
        self.settings.setValue("language", lang)
        i18n.set_language(lang)
        self.language_changed.emit(lang)
        self._update_selection_buttons()

    def _set_theme(self, theme: str):
        self.current_theme = theme
        self.theme_changed.emit(theme)
        self._update_selection_buttons()

    def _update_selection_buttons(self):
        # Language highlights
        is_vi = (i18n.current_language == "vi")
        self.btn_lang_vi.setStyleSheet("background: rgba(32,184,242,0.18); border: 1.5px solid #20b8f2; color: #b8efff; font-weight: 700; border-radius: 7px;" if is_vi else "background: rgba(255,255,255,0.035); border: 1px solid rgba(213,225,240,0.1); border-radius: 7px; color: #9dacbd;")
        self.btn_lang_en.setStyleSheet("background: rgba(32,184,242,0.18); border: 1.5px solid #20b8f2; color: #b8efff; font-weight: 700; border-radius: 7px;" if not is_vi else "background: rgba(255,255,255,0.035); border: 1px solid rgba(213,225,240,0.1); border-radius: 7px; color: #9dacbd;")

        # Theme highlights
        is_dark = (self.current_theme == "dark")
        self.btn_theme_dark.setStyleSheet("background: rgba(32,184,242,0.18); border: 1.5px solid #20b8f2; color: #b8efff; font-weight: 700; border-radius: 7px;" if is_dark else "background: rgba(255,255,255,0.035); border: 1px solid rgba(213,225,240,0.1); border-radius: 7px; color: #9dacbd;")
        self.btn_theme_light.setStyleSheet("background: rgba(32,184,242,0.18); border: 1.5px solid #20b8f2; color: #b8efff; font-weight: 700; border-radius: 7px;" if not is_dark else "background: rgba(255,255,255,0.035); border: 1px solid rgba(213,225,240,0.1); border-radius: 7px; color: #9dacbd;")

    def retranslate(self):
        self.lbl_title.setText(i18n["settingsTitle"])
        self.lbl_sub.setText(i18n["settingsSub"])
        self.card_lang.retranslate()
        self.card_theme.retranslate()
        self.card_fw.retranslate()
        self.card_startup.retranslate()
        self.card_data.retranslate()
        self.btn_theme_dark.setText(f"🌙  {i18n['dark']}")
        self.btn_theme_light.setText(f"☀️  {i18n['light']}")
        self.chk_auto_uac.setText(i18n["autoUac"])
        self.chk_notify.setText(i18n["notify"])
        self.chk_startup.setText(i18n["startWindows"])
        self.chk_tray.setText(i18n["tray"])
        self._update_selection_buttons()
