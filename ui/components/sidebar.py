from PyQt6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QWidget
)
from PyQt6.QtCore import Qt, pyqtSignal
from core.i18n import i18n


class Sidebar(QFrame):
    """
    Operational Rail Sidebar matching Fluent Control Room layout.
    """

    page_changed = pyqtSignal(str)  # 'processes', 'traffic', 'profiles', 'settings'

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("Sidebar")
        self.setFixedWidth(230)
        self._is_collapsed = False
        self._current_page = "processes"

        self._setup_ui()
        i18n.language_changed.connect(self.retranslate)

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 20, 14, 16)
        layout.setSpacing(12)

        # Brand Header
        self.brand_container = QWidget()
        brand_layout = QHBoxLayout(self.brand_container)
        brand_layout.setContentsMargins(4, 0, 4, 0)
        brand_layout.setSpacing(10)

        self.lbl_logo = QLabel("⚡")
        self.lbl_logo.setStyleSheet("font-size: 20px; color: #20b8f2;")

        self.brand_text_box = QWidget()
        text_layout = QVBoxLayout(self.brand_text_box)
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(1)

        self.lbl_brand_title = QLabel("Kayzit NetManager")
        self.lbl_brand_title.setObjectName("SidebarBrandTitle")
        self.lbl_brand_sub = QLabel(i18n["controlRoom"])
        self.lbl_brand_sub.setObjectName("SidebarBrandSub")

        text_layout.addWidget(self.lbl_brand_title)
        text_layout.addWidget(self.lbl_brand_sub)

        brand_layout.addWidget(self.lbl_logo)
        brand_layout.addWidget(self.brand_text_box, stretch=1)
        layout.addWidget(self.brand_container)

        # Divider
        divider = QFrame()
        divider.setFixedHeight(1)
        divider.setStyleSheet("background-color: rgba(213, 225, 240, 0.10); margin: 6px 0px;")
        layout.addWidget(divider)

        # Nav Items
        self.btn_processes = self._create_nav_button("📊", i18n["processes"], "processes")
        self.btn_traffic = self._create_nav_button("📈", i18n["traffic"], "traffic")
        self.btn_profiles = self._create_nav_button("🛡️", i18n["profiles"], "profiles")
        self.btn_settings = self._create_nav_button("⚙️", i18n["settings"], "settings")

        layout.addWidget(self.btn_processes)
        layout.addWidget(self.btn_traffic)
        layout.addWidget(self.btn_profiles)
        layout.addWidget(self.btn_settings)

        layout.addStretch(1)

        # Service Online Card
        self.service_card = QFrame()
        self.service_card.setObjectName("ServiceCard")
        svc_layout = QVBoxLayout(self.service_card)
        svc_layout.setContentsMargins(10, 10, 10, 10)
        svc_layout.setSpacing(4)

        self.lbl_svc_status = QLabel(f"🟢 {i18n['online']}")
        self.lbl_svc_status.setStyleSheet("color: #41e6a5; font-size: 10px; font-weight: 700; letter-spacing: 0.8px;")
        self.lbl_svc_desc = QLabel(i18n["onlineDesc"])
        self.lbl_svc_desc.setStyleSheet("color: #8e99a9; font-size: 11px;")
        self.lbl_svc_desc.setWordWrap(True)

        svc_layout.addWidget(self.lbl_svc_status)
        svc_layout.addWidget(self.lbl_svc_desc)
        layout.addWidget(self.service_card)

        # Collapse Button
        self.btn_collapse = QPushButton("◀")
        self.btn_collapse.setObjectName("QuietBtn")
        self.btn_collapse.setFixedHeight(32)
        self.btn_collapse.clicked.connect(self._toggle_collapse)
        layout.addWidget(self.btn_collapse)

        # Set default active
        self._set_active_page("processes")

    def _create_nav_button(self, icon: str, title: str, page_id: str) -> QPushButton:
        btn = QPushButton(f"{icon}   {title}")
        btn.setObjectName("NavItem")
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setFixedHeight(42)
        btn.clicked.connect(lambda: self._on_nav_clicked(page_id))
        return btn

    def _on_nav_clicked(self, page_id: str):
        self._set_active_page(page_id)
        self.page_changed.emit(page_id)

    def _set_active_page(self, page_id: str):
        self._current_page = page_id
        for btn, pid in [
            (self.btn_processes, "processes"),
            (self.btn_traffic, "traffic"),
            (self.btn_profiles, "profiles"),
            (self.btn_settings, "settings")
        ]:
            is_active = (pid == page_id)
            btn.setProperty("active", "true" if is_active else "false")
            btn.style().unpolish(btn)
            btn.style().polish(btn)

    def update_process_count(self, count: int):
        self.btn_processes.setText(f"📊   {i18n['processes']}   ({count})")

    def _toggle_collapse(self):
        self._is_collapsed = not self._is_collapsed
        if self._is_collapsed:
            self.setFixedWidth(70)
            self.brand_text_box.hide()
            self.service_card.hide()
            self.btn_processes.setText("📊")
            self.btn_traffic.setText("📈")
            self.btn_profiles.setText("🛡️")
            self.btn_settings.setText("⚙️")
            self.btn_collapse.setText("▶")
        else:
            self.setFixedWidth(230)
            self.brand_text_box.show()
            self.service_card.show()
            self.btn_processes.setText(f"📊   {i18n['processes']}")
            self.btn_traffic.setText(f"📈   {i18n['traffic']}")
            self.btn_profiles.setText(f"🛡️   {i18n['profiles']}")
            self.btn_settings.setText(f"⚙️   {i18n['settings']}")
            self.btn_collapse.setText("◀")

    def retranslate(self):
        self.lbl_brand_sub.setText(i18n["controlRoom"])
        if not self._is_collapsed:
            self.btn_processes.setText(f"📊   {i18n['processes']}")
            self.btn_traffic.setText(f"📈   {i18n['traffic']}")
            self.btn_profiles.setText(f"🛡️   {i18n['profiles']}")
            self.btn_settings.setText(f"⚙️   {i18n['settings']}")
        self.lbl_svc_status.setText(f"🟢 {i18n['online']}")
        self.lbl_svc_desc.setText(i18n["onlineDesc"])
