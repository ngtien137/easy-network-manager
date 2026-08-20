"""
Fluent Control Room Theme System for PyQt6.
Matches the exact graphite surface colors, Signal Cyan accents, and typography of the Web Demo.
"""

DARK_THEME = """
/* Global Window Base */
QWidget {
    background-color: #0d0f13;
    color: #f2f7fc;
    font-family: 'Segoe UI Variable Text', 'Segoe UI', 'Manrope', system-ui, sans-serif;
    font-size: 13px;
    selection-background-color: #20b8f2;
    selection-color: #05202a;
}

/* Sidebar */
QFrame#Sidebar {
    background-color: #101318;
    border-right: 1px solid rgba(213, 225, 240, 0.10);
}

QLabel#SidebarBrandTitle {
    font-family: 'Space Grotesk', 'Segoe UI', sans-serif;
    font-size: 16px;
    font-weight: 700;
    color: #f2f7fc;
    letter-spacing: -0.5px;
}

QLabel#SidebarBrandSub {
    font-size: 9px;
    font-weight: 700;
    color: #667181;
    letter-spacing: 1px;
}

QPushButton#NavItem {
    background-color: transparent;
    color: #98a5b6;
    border: 1px solid transparent;
    border-radius: 8px;
    padding: 10px 14px;
    text-align: left;
    font-size: 13px;
    font-weight: 600;
}

QPushButton#NavItem:hover {
    background-color: rgba(255, 255, 255, 0.04);
    color: #f2f7fc;
}

QPushButton#NavItem[active="true"] {
    background-color: rgba(32, 184, 242, 0.14);
    color: #b8efff;
    border: 1px solid rgba(32, 184, 242, 0.32);
}

/* Service Online Card */
QFrame#ServiceCard {
    background-color: rgba(32, 184, 242, 0.06);
    border: 1px solid rgba(32, 184, 242, 0.20);
    border-radius: 10px;
    padding: 10px 12px;
}

/* Topbar */
QFrame#Topbar {
    background-color: rgba(13, 15, 19, 0.90);
    border-bottom: 1px solid rgba(213, 225, 240, 0.10);
}

/* Search Bar */
QLineEdit#GlobalSearch, QLineEdit#TableSearch {
    background-color: rgba(255, 255, 255, 0.035);
    color: #f2f7fc;
    border: 1px solid rgba(213, 225, 240, 0.10);
    border-radius: 8px;
    padding: 8px 14px;
    font-size: 13px;
}

QLineEdit#GlobalSearch:focus, QLineEdit#TableSearch:focus {
    border: 1.5px solid #20b8f2;
    background-color: rgba(32, 184, 242, 0.06);
}

QLineEdit::placeholder {
    color: #647080;
}

/* Top Action Buttons */
QPushButton#TopActionBtn, QPushButton#QuietBtn {
    background-color: rgba(255, 255, 255, 0.035);
    color: #b7c3d1;
    border: 1px solid rgba(213, 225, 240, 0.10);
    border-radius: 8px;
    padding: 6px 12px;
    font-size: 12px;
    font-weight: 600;
}

QPushButton#TopActionBtn:hover, QPushButton#QuietBtn:hover {
    color: #85e4ff;
    border-color: rgba(32, 184, 242, 0.45);
    background-color: rgba(32, 184, 242, 0.08);
}

/* Primary Action (Signal Cyan) */
QPushButton#PrimaryActionBtn {
    background-color: #20b8f2;
    color: #05202a;
    border: none;
    border-radius: 7px;
    padding: 8px 16px;
    font-size: 12px;
    font-weight: 700;
}

QPushButton#PrimaryActionBtn:hover {
    background-color: #38c8ff;
}

QPushButton#PrimaryActionBtn:disabled {
    background-color: #2a3b47;
    color: #647080;
}

/* KPI Metric Cards */
QFrame#MetricCard {
    background-color: #171a21;
    border: 1px solid rgba(213, 225, 240, 0.10);
    border-radius: 11px;
    padding: 14px 16px;
}

QFrame#MetricCard:hover {
    border: 1px solid rgba(213, 225, 240, 0.18);
    background-color: #1c2029;
}

QLabel#MetricLabel {
    font-family: 'Space Grotesk', 'Segoe UI', sans-serif;
    font-size: 10px;
    font-weight: 700;
    color: #8e99a9;
    letter-spacing: 0.8px;
    text-transform: uppercase;
}

QLabel#MetricValue {
    font-family: 'Space Grotesk', 'Segoe UI', sans-serif;
    font-size: 24px;
    font-weight: 700;
    color: #f2f7fc;
    letter-spacing: -0.8px;
}

QLabel#MetricNote {
    font-size: 11px;
    color: #768394;
}

/* Filter Tabs */
QFrame#FilterTabsFrame {
    background-color: rgba(0, 0, 0, 0.20);
    border: 1px solid rgba(213, 225, 240, 0.10);
    border-radius: 8px;
    padding: 2px;
}

QPushButton#FilterTabBtn {
    background-color: transparent;
    color: #8e99a9;
    border: none;
    border-radius: 6px;
    padding: 5px 14px;
    font-size: 11px;
    font-weight: 600;
}

QPushButton#FilterTabBtn:hover {
    color: #f2f7fc;
}

QPushButton#FilterTabBtn[active="true"] {
    background-color: rgba(32, 184, 242, 0.16);
    color: #b8efff;
}

/* Table Panel & Tree Widget */
QFrame#TablePanel {
    background-color: #171a21;
    border: 1px solid rgba(213, 225, 240, 0.10);
    border-radius: 11px;
}

QTreeWidget {
    background-color: #171a21;
    border: none;
    padding: 0px;
    alternate-background-color: #15181f;
}

QTreeWidget::item {
    min-height: 38px;
    height: 38px;
    padding: 2px 8px;
    border-bottom: 1px solid rgba(213, 225, 240, 0.05);
    color: #c8d2df;
}

QTreeWidget::item:hover {
    background-color: rgba(255, 255, 255, 0.035);
    color: #f2f7fc;
}

QTreeWidget::item:selected {
    background-color: rgba(32, 184, 242, 0.14);
    color: #ffffff;
}

QHeaderView::section {
    background-color: #12151b;
    color: #748091;
    padding: 10px 12px;
    border: none;
    border-bottom: 1px solid rgba(213, 225, 240, 0.10);
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.75px;
    text-transform: uppercase;
}

/* Scrollbars */
QScrollBar:vertical {
    border: none;
    background-color: #101318;
    width: 8px;
    margin: 0px;
    border-radius: 4px;
}

QScrollBar::handle:vertical {
    background-color: #272d38;
    min-height: 25px;
    border-radius: 4px;
}

QScrollBar::handle:vertical:hover {
    background-color: #384252;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    border: none;
    background: none;
}

/* Eyebrow & Headings */
QLabel#Eyebrow {
    font-family: 'Space Grotesk', 'Segoe UI', sans-serif;
    font-size: 10px;
    font-weight: 700;
    color: #7790a6;
    letter-spacing: 1.25px;
    text-transform: uppercase;
}

QLabel#PageTitle {
    font-family: 'Space Grotesk', 'Segoe UI', sans-serif;
    font-size: 26px;
    font-weight: 700;
    color: #f2f7fc;
    letter-spacing: -0.8px;
}

QLabel#PageSubtitle {
    font-size: 13px;
    color: #8e99a9;
}

/* Profile & Setting Cards */
QFrame#ProfileCard, QFrame#SettingCard {
    background-color: #171a21;
    border: 1px solid rgba(213, 225, 240, 0.10);
    border-radius: 12px;
    padding: 18px 20px;
}

QFrame#ProfileCard:hover, QFrame#SettingCard:hover {
    border-color: rgba(213, 225, 240, 0.18);
    background-color: #1c2029;
}

/* Footer & Status Chips */
QLabel#AdminChip {
    background-color: rgba(65, 230, 165, 0.09);
    color: #82f1cb;
    border: 1px solid rgba(65, 230, 165, 0.28);
    border-radius: 6px;
    padding: 4px 8px;
    font-size: 11px;
    font-weight: 700;
}
"""

LIGHT_THEME = """
QWidget {
    background-color: #f3f6fa;
    color: #18222e;
    font-family: 'Segoe UI Variable Text', 'Segoe UI', 'Manrope', system-ui, sans-serif;
    font-size: 13px;
}

QFrame#Sidebar {
    background-color: #ffffff;
    border-right: 1px solid rgba(49, 72, 99, 0.12);
}

QLabel#SidebarBrandTitle {
    color: #18222e;
}

QPushButton#NavItem {
    color: #637386;
}

QPushButton#NavItem:hover {
    background-color: #f0f5fa;
    color: #18222e;
}

QPushButton#NavItem[active="true"] {
    background-color: rgba(32, 184, 242, 0.12);
    color: #0284c7;
    border: 1px solid rgba(32, 184, 242, 0.25);
}

QFrame#Topbar {
    background-color: #ffffff;
    border-bottom: 1px solid rgba(49, 72, 99, 0.12);
}

QLineEdit#GlobalSearch, QLineEdit#TableSearch {
    background-color: #ffffff;
    color: #18222e;
    border: 1px solid rgba(49, 72, 99, 0.16);
}

QFrame#MetricCard, QFrame#TablePanel, QFrame#ProfileCard, QFrame#SettingCard {
    background-color: #ffffff;
    border: 1px solid rgba(49, 72, 99, 0.12);
}

QTreeWidget {
    background-color: #ffffff;
    color: #18222e;
}

QHeaderView::section {
    background-color: #f8fafc;
    color: #64748b;
    border-bottom: 1px solid rgba(49, 72, 99, 0.12);
}
"""


class ThemeManager:
    """Manages switching between Fluent Control Room Dark and Light themes."""

    @staticmethod
    def apply_theme(app, theme_name: str = "dark"):
        if theme_name == "light":
            app.setStyleSheet(LIGHT_THEME)
        else:
            app.setStyleSheet(DARK_THEME)
