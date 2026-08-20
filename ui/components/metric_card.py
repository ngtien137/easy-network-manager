from PyQt6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QWidget
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QPainter, QBrush, QPen


class ProgressTrack(QWidget):
    """Mini progress track bar with custom tone color."""
    def __init__(self, color_hex: str = "#20b8f2", parent=None):
        super().__init__(parent)
        self.color_hex = color_hex
        self.percent = 0.0
        self.setFixedHeight(3)

    def set_percent(self, pct: float):
        self.percent = max(0.0, min(100.0, pct))
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Track background
        painter.setBrush(QBrush(QColor(255, 255, 255, 20)))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(0, 0, self.width(), self.height(), 2, 2)

        # Active fill
        fill_w = int(self.width() * (self.percent / 100.0))
        if fill_w > 0:
            painter.setBrush(QBrush(QColor(self.color_hex)))
            painter.drawRoundedRect(0, 0, fill_w, self.height(), 2, 2)
        painter.end()


class MetricCard(QFrame):
    """
    KPI Metric Card matching the Fluent Control Room design.
    """
    def __init__(self, label: str, icon_str: str, tone_color: str = "#20b8f2", parent=None):
        super().__init__(parent)
        self.setObjectName("MetricCard")
        self.tone_color = tone_color

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(6)

        # Heading Row (Label + Icon)
        head_row = QHBoxLayout()
        self.lbl_title = QLabel(label)
        self.lbl_title.setObjectName("MetricLabel")

        self.lbl_icon = QLabel(icon_str)
        self.lbl_icon.setStyleSheet(f"""
            QLabel {{
                background-color: {tone_color}22;
                color: {tone_color};
                border-radius: 6px;
                padding: 4px 6px;
                font-weight: bold;
                font-size: 13px;
            }}
        """)

        head_row.addWidget(self.lbl_title)
        head_row.addStretch(1)
        head_row.addWidget(self.lbl_icon)
        layout.addLayout(head_row)

        # Value
        self.lbl_value = QLabel("0")
        self.lbl_value.setObjectName("MetricValue")
        layout.addWidget(self.lbl_value)

        # Note
        self.lbl_note = QLabel("")
        self.lbl_note.setObjectName("MetricNote")
        layout.addWidget(self.lbl_note)

        # Progress Track
        self.track = ProgressTrack(tone_color, self)
        layout.addWidget(self.track)

    def set_data(self, value: str, note: str, percent: float):
        self.lbl_value.setText(value)
        self.lbl_note.setText(note)
        self.track.set_percent(percent)

    def set_title(self, title: str):
        self.lbl_title.setText(title)
