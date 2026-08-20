"""
UI package for NetworkManager application.
Contains themes, custom widgets, views, and main window.
"""

from .theme import ThemeManager, DARK_THEME, LIGHT_THEME
from .main_window import MainWindow

__all__ = ["ThemeManager", "DARK_THEME", "LIGHT_THEME", "MainWindow"]
