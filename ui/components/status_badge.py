from PyQt6.QtWidgets import QLabel
from PyQt6.QtCore import Qt
from core.models import NetworkState
from core.i18n import i18n


class StatusBadge(QLabel):
    """
    Visual indicator badge for process network status (🟢 Allowed vs 🔴 Blocked).
    """

    def __init__(self, state: NetworkState = NetworkState.ALLOWED, parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setFixedHeight(24)
        self.setMinimumWidth(85)
        self._current_state = state
        self.set_state(state)
        i18n.language_changed.connect(self._on_lang_changed)

    def set_state(self, state: NetworkState):
        """Update badge appearance and text according to network state."""
        self._current_state = state
        if state == NetworkState.BLOCKED:
            self.setText(f"🔴 {i18n['blockedStatus']}")
            self.setStyleSheet("""
                QLabel {
                    background-color: rgba(239, 68, 68, 0.18);
                    color: #ff9b9b;
                    border: 1px solid rgba(239, 68, 68, 0.4);
                    border-radius: 12px;
                    padding: 2px 10px;
                    font-size: 11px;
                    font-weight: 700;
                }
            """)
        elif state == NetworkState.ALLOWED:
            self.setText(f"🟢 {i18n['allowed']}")
            self.setStyleSheet("""
                QLabel {
                    background-color: rgba(65, 230, 165, 0.15);
                    color: #77edc4;
                    border: 1px solid rgba(65, 230, 165, 0.35);
                    border-radius: 12px;
                    padding: 2px 10px;
                    font-size: 11px;
                    font-weight: 700;
                }
            """)
        elif state == NetworkState.SYSTEM:
            self.setText(f"🛡️ {i18n['system']}")
            self.setStyleSheet("""
                QLabel {
                    background-color: rgba(172, 182, 196, 0.10);
                    color: #acb6c4;
                    border: 1px solid rgba(172, 182, 196, 0.25);
                    border-radius: 12px;
                    padding: 2px 10px;
                    font-size: 11px;
                    font-weight: 600;
                }
            """)
        else:
            self.setText("⚪ Unknown")
            self.setStyleSheet("""
                QLabel {
                    background-color: rgba(161, 161, 170, 0.15);
                    color: #a1a1aa;
                    border: 1px solid rgba(161, 161, 170, 0.3);
                    border-radius: 12px;
                    padding: 2px 10px;
                    font-size: 11px;
                    font-weight: 500;
                }
            """)

    def _on_lang_changed(self):
        self.set_state(self._current_state)
