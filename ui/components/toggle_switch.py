from PyQt6.QtWidgets import QCheckBox
from PyQt6.QtCore import Qt, QRectF, pyqtProperty, QPropertyAnimation, QEasingCurve, pyqtSignal
from PyQt6.QtGui import QPainter, QColor, QBrush, QPen


class ToggleSwitch(QCheckBox):
    """
    Windows 11 style animated Toggle Switch widget.
    Checked state (True) = Blocked (Red accent).
    Unchecked state (False) = Allowed (Gray/Neutral accent).
    """

    toggled_with_item = pyqtSignal(bool, object)  # (is_blocked, item_ref)

    def __init__(self, item_ref=None, parent=None):
        super().__init__(parent)
        self.item_ref = item_ref
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedSize(46, 24)

        # Animation position offset
        self._thumb_position = 3.0
        self._anim = QPropertyAnimation(self, b"thumb_position", self)
        self._anim.setDuration(160)
        self._anim.setEasingCurve(QEasingCurve.Type.InOutCubic)

        self.toggled.connect(self._handle_toggled)

    @pyqtProperty(float)
    def thumb_position(self) -> float:
        return self._thumb_position

    @thumb_position.setter
    def thumb_position(self, pos: float):
        self._thumb_position = pos
        self.update()

    def _handle_toggled(self, checked: bool):
        self._anim.stop()
        if checked:
            self._anim.setStartValue(self._thumb_position)
            self._anim.setEndValue(25.0)
        else:
            self._anim.setStartValue(self._thumb_position)
            self._anim.setEndValue(3.0)
        self._anim.start()
        self.toggled_with_item.emit(checked, self.item_ref)

    def setCheckedSilently(self, checked: bool):
        """Set checked state without firing animation or signals if unchanged."""
        self.blockSignals(True)
        self.setChecked(checked)
        self._thumb_position = 25.0 if checked else 3.0
        self.blockSignals(False)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Background track
        track_rect = QRectF(0, 2, 44, 20)
        if self.isChecked():
            # Blocked (Red active)
            track_color = QColor("#ef4444")
            border_color = QColor("#dc2626")
        else:
            # Normal / Allowed (Subtle dark track)
            track_color = QColor("#3f3f46")
            border_color = QColor("#52525b")

        painter.setBrush(QBrush(track_color))
        painter.setPen(QPen(border_color, 1))
        painter.drawRoundedRect(track_rect, 10, 10)

        # Thumb circle
        thumb_rect = QRectF(self._thumb_position, 4, 16, 16)
        painter.setBrush(QBrush(QColor("#ffffff")))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(thumb_rect)

        painter.end()
