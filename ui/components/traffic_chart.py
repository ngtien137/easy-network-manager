import time
from collections import deque
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QPainterPath, QLinearGradient, QFont


class TrafficChartWidget(QWidget):
    """
    Real-time Live Throughput Chart with smooth spline curve and gradient area fill.
    Draws Green line for Download and Signal Cyan line for Upload.
    """

    def __init__(self, max_points: int = 35, parent=None):
        super().__init__(parent)
        self.max_points = max_points
        self.setMinimumHeight(160)

        # History buffers (in KB/s)
        self.dl_history = deque([10.0] * max_points, maxlen=max_points)
        self.ul_history = deque([2.0] * max_points, maxlen=max_points)

    def add_sample(self, dl_bytes_sec: float, ul_bytes_sec: float):
        dl_kb = dl_bytes_sec / 1024.0
        ul_kb = ul_bytes_sec / 1024.0
        self.dl_history.append(dl_kb)
        self.ul_history.append(ul_kb)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = self.width()
        h = self.height()
        padding_left = 45
        padding_bottom = 22
        padding_top = 10
        padding_right = 10

        chart_w = w - padding_left - padding_right
        chart_h = h - padding_top - padding_bottom

        if chart_w <= 10 or chart_h <= 10:
            painter.end()
            return

        # Calculate max scale
        max_val = max(max(self.dl_history), max(self.ul_history), 50.0)  # at least 50 KB/s
        max_val = max_val * 1.2  # margin

        # Draw Grid Lines & Y Labels
        painter.setPen(QPen(QColor(255, 255, 255, 15), 1, Qt.PenStyle.DashLine))
        font = QFont("Segoe UI", 8)
        painter.setFont(font)

        steps = 3
        for i in range(steps + 1):
            y = padding_top + chart_h - (i * (chart_h / steps))
            painter.drawLine(int(padding_left), int(y), int(w - padding_right), int(y))
            
            # Label
            val_at_y = (i / steps) * max_val
            if val_at_y >= 1024:
                val_str = f"{val_at_y/1024:.1f} MB/s"
            else:
                val_str = f"{val_at_y:.0f} KB/s"
            painter.setPen(QColor("#667488"))
            painter.drawText(2, int(y + 4), val_str)
            painter.setPen(QPen(QColor(255, 255, 255, 15), 1, Qt.PenStyle.DashLine))

        # Build Points for Download
        dl_points = []
        ul_points = []
        n = len(self.dl_history)
        step_x = chart_w / max(n - 1, 1)

        for idx in range(n):
            x = padding_left + (idx * step_x)
            
            # Download Y
            dl_val = self.dl_history[idx]
            dl_y = padding_top + chart_h - ((dl_val / max_val) * chart_h)
            dl_points.append(QPointF(x, max(padding_top, min(dl_y, padding_top + chart_h))))

            # Upload Y
            ul_val = self.ul_history[idx]
            ul_y = padding_top + chart_h - ((ul_val / max_val) * chart_h)
            ul_points.append(QPointF(x, max(padding_top, min(ul_y, padding_top + chart_h))))

        # Draw Download Area Fill
        if len(dl_points) > 1:
            fill_path = QPainterPath()
            fill_path.moveTo(padding_left, padding_top + chart_h)
            for pt in dl_points:
                fill_path.lineTo(pt)
            fill_path.lineTo(dl_points[-1].x(), padding_top + chart_h)
            fill_path.closeSubpath()

            grad = QLinearGradient(0, padding_top, 0, padding_top + chart_h)
            grad.setColorAt(0.0, QColor(65, 230, 165, 60))
            grad.setColorAt(1.0, QColor(65, 230, 165, 0))
            painter.fillPath(fill_path, QBrush(grad))

            # Draw Download Stroke
            dl_path = QPainterPath()
            dl_path.moveTo(dl_points[0])
            for pt in dl_points[1:]:
                dl_path.lineTo(pt)
            painter.setPen(QPen(QColor("#41e6a5"), 2.2))
            painter.drawPath(dl_path)

        # Draw Upload Stroke
        if len(ul_points) > 1:
            ul_path = QPainterPath()
            ul_path.moveTo(ul_points[0])
            for pt in ul_points[1:]:
                ul_path.lineTo(pt)
            painter.setPen(QPen(QColor("#20b8f2"), 2.2))
            painter.drawPath(ul_path)

        # Draw X-Axis Time Labels
        painter.setPen(QColor("#607084"))
        painter.drawText(int(padding_left), int(h - 4), "-1m")
        painter.drawText(int(padding_left + chart_w * 0.5 - 10), int(h - 4), "-30s")
        painter.drawText(int(w - padding_right - 24), int(h - 4), "Now")

        painter.end()
