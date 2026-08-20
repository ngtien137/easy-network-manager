from typing import List
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QTreeWidget, QTreeWidgetItem, QHeaderView
)
from PyQt6.QtCore import Qt, pyqtSignal

from core.models import SocketConnection, SystemResourceSummary
from core.i18n import i18n
from ui.components.traffic_chart import TrafficChartWidget


class TrafficView(QWidget):
    """
    Real-time Network Traffic and Socket Observability View.
    """

    block_socket_requested = pyqtSignal(object)  # (SocketConnection)
    refresh_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._sockets: List[SocketConnection] = []
        self._setup_ui()
        i18n.language_changed.connect(self.retranslate)

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(28, 24, 28, 20)
        main_layout.setSpacing(16)

        # 1. Page Heading
        heading_layout = QHBoxLayout()
        title_box = QVBoxLayout()
        title_box.setSpacing(4)

        self.lbl_eyebrow = QLabel("FLOW OBSERVABILITY")
        self.lbl_eyebrow.setObjectName("Eyebrow")

        self.lbl_title = QLabel(i18n["trafficTitle"])
        self.lbl_title.setObjectName("PageTitle")

        self.lbl_sub = QLabel(i18n["trafficSub"])
        self.lbl_sub.setObjectName("PageSubtitle")

        title_box.addWidget(self.lbl_eyebrow)
        title_box.addWidget(self.lbl_title)
        title_box.addWidget(self.lbl_sub)
        heading_layout.addLayout(title_box, stretch=1)

        # Segmented timeframe buttons
        seg_frame = QFrame()
        seg_frame.setObjectName("FilterTabsFrame")
        seg_l = QHBoxLayout(seg_frame)
        seg_l.setContentsMargins(3, 3, 3, 3)
        seg_l.setSpacing(4)

        self.btn_1m = QPushButton(i18n["minute"])
        self.btn_1m.setObjectName("FilterTabBtn")
        self.btn_1m.setProperty("active", "true")

        self.btn_5m = QPushButton(i18n["fiveMinutes"])
        self.btn_5m.setObjectName("FilterTabBtn")

        self.btn_15m = QPushButton(i18n["fifteenMinutes"])
        self.btn_15m.setObjectName("FilterTabBtn")

        seg_l.addWidget(self.btn_1m)
        seg_l.addWidget(self.btn_5m)
        seg_l.addWidget(self.btn_15m)
        heading_layout.addWidget(seg_frame, alignment=Qt.AlignmentFlag.AlignTop)

        main_layout.addLayout(heading_layout)

        # 2. Top Traffic Grid (Chart Card + Summary Card)
        grid_layout = QHBoxLayout()
        grid_layout.setSpacing(14)

        # Chart Card
        self.chart_card = QFrame()
        self.chart_card.setObjectName("MetricCard")
        chart_l = QVBoxLayout(self.chart_card)
        chart_l.setContentsMargins(18, 16, 18, 14)
        chart_l.setSpacing(8)

        # Chart Header Stats
        ch_head = QHBoxLayout()
        ch_title_box = QVBoxLayout()
        ch_title_box.setSpacing(2)
        lbl_throughput_title = QLabel("NETWORK THROUGHPUT")
        lbl_throughput_title.setObjectName("Eyebrow")
        self.lbl_throughput_val = QLabel("0.0 MB/s")
        self.lbl_throughput_val.setObjectName("MetricValue")
        ch_title_box.addWidget(lbl_throughput_title)
        ch_title_box.addWidget(self.lbl_throughput_val)

        ch_rates = QHBoxLayout()
        self.lbl_dl_rate = QLabel("↓ 0 KB/s")
        self.lbl_dl_rate.setStyleSheet("color: #41e6a5; font-weight: 700; font-size: 11px;")
        self.lbl_ul_rate = QLabel("↑ 0 KB/s")
        self.lbl_ul_rate.setStyleSheet("color: #20b8f2; font-weight: 700; font-size: 11px;")
        ch_rates.addWidget(self.lbl_dl_rate)
        ch_rates.addWidget(self.lbl_ul_rate)

        ch_head.addLayout(ch_title_box)
        ch_head.addStretch(1)
        ch_head.addLayout(ch_rates)
        chart_l.addLayout(ch_head)

        # Chart Canvas
        self.chart_canvas = TrafficChartWidget(parent=self.chart_card)
        chart_l.addWidget(self.chart_canvas, stretch=1)

        # Chart Legend
        leg_layout = QHBoxLayout()
        self.lbl_leg_dl = QLabel(f"🟢 {i18n['download']}")
        self.lbl_leg_dl.setStyleSheet("color: #a4b2c1; font-size: 11px;")
        self.lbl_leg_ul = QLabel(f"🔵 {i18n['upload']}")
        self.lbl_leg_ul.setStyleSheet("color: #a4b2c1; font-size: 11px;")
        self.lbl_live = QLabel("🔴 LIVE")
        self.lbl_live.setStyleSheet("color: #41e6a5; font-size: 10px; font-weight: 700; letter-spacing: 0.8px;")

        leg_layout.addWidget(self.lbl_leg_dl)
        leg_layout.addWidget(self.lbl_leg_ul)
        leg_layout.addStretch(1)
        leg_layout.addWidget(self.lbl_live)
        chart_l.addLayout(leg_layout)

        grid_layout.addWidget(self.chart_card, stretch=3)

        # Socket Summary Card
        self.summary_card = QFrame()
        self.summary_card.setObjectName("MetricCard")
        self.summary_card.setFixedWidth(240)
        self.summary_card.setStyleSheet("background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 rgba(32,184,242,0.12), stop:1 rgba(23,26,33,0.88));")
        sum_l = QVBoxLayout(self.summary_card)
        sum_l.setContentsMargins(18, 18, 18, 16)
        sum_l.setSpacing(8)

        lbl_sum_eyebrow = QLabel("SOCKET SUMMARY")
        lbl_sum_eyebrow.setObjectName("Eyebrow")
        self.lbl_sum_count = QLabel("0")
        self.lbl_sum_count.setObjectName("MetricValue")
        self.lbl_sum_count.setStyleSheet("font-size: 32px; font-weight: 700; color: #f2f7fc;")
        self.lbl_sum_note = QLabel(i18n["connected"])
        self.lbl_sum_note.setStyleSheet("color: #90a0b1; font-size: 11px;")

        sum_l.addWidget(lbl_sum_eyebrow)
        sum_l.addWidget(self.lbl_sum_count)
        sum_l.addWidget(self.lbl_sum_note)
        sum_l.addStretch(1)

        btn_refresh_list = QPushButton(f"🔄 {i18n['refresh']}")
        btn_refresh_list.setObjectName("QuietBtn")
        btn_refresh_list.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_refresh_list.clicked.connect(self.refresh_requested.emit)
        sum_l.addWidget(btn_refresh_list)

        grid_layout.addWidget(self.summary_card, stretch=1)
        main_layout.addLayout(grid_layout)

        # 3. Active Sockets Table Panel
        self.socket_panel = QFrame()
        self.socket_panel.setObjectName("TablePanel")
        sock_panel_l = QVBoxLayout(self.socket_panel)
        sock_panel_l.setContentsMargins(1, 1, 1, 1)
        sock_panel_l.setSpacing(0)

        # Sockets Panel Header
        sock_header = QFrame()
        sock_header.setStyleSheet("border-bottom: 1px solid rgba(213, 225, 240, 0.10); padding: 12px 16px;")
        sh_l = QHBoxLayout(sock_header)
        sh_l.setContentsMargins(0, 0, 0, 0)

        sh_title_box = QVBoxLayout()
        sh_title_box.setSpacing(2)
        self.lbl_sock_title = QLabel(i18n["activeSockets"])
        self.lbl_sock_title.setObjectName("Eyebrow")
        self.lbl_sock_sub = QLabel("TCP / UDP · Live observed destinations")
        self.lbl_sock_sub.setStyleSheet("color: #8e99a9; font-size: 11px;")
        sh_title_box.addWidget(self.lbl_sock_title)
        sh_title_box.addWidget(self.lbl_sock_sub)

        sh_l.addLayout(sh_title_box)
        sh_l.addStretch(1)
        sock_panel_l.addWidget(sock_header)

        # Sockets Tree
        self.sock_tree = QTreeWidget()
        self.sock_tree.setHeaderLabels([
            i18n["process"], i18n["local"], i18n["remote"], i18n["protocol"], i18n["state"], i18n["action"]
        ])
        self.sock_tree.header().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.sock_tree.header().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.sock_tree.header().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.sock_tree.header().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.sock_tree.header().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        self.sock_tree.header().setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)

        self.sock_tree.setRootIsDecorated(False)
        sock_panel_l.addWidget(self.sock_tree, stretch=1)

        main_layout.addWidget(self.socket_panel, stretch=1)

    def update_telemetry(self, summary: SystemResourceSummary, sockets: List[SocketConnection]):
        self._sockets = sockets
        # Update Throughput Labels
        self.lbl_throughput_val.setText(summary.download_speed)
        self.lbl_dl_rate.setText(f"↓ {summary.download_speed}")
        self.lbl_ul_rate.setText(f"↑ {summary.upload_speed}")
        self.lbl_sum_count.setText(str(len(sockets)))

        # Update Chart Canvas
        self.chart_canvas.add_sample(summary.download_bytes_sec, summary.upload_bytes_sec)

        # Update Sockets Tree
        self.sock_tree.clear()
        for s in sockets[:40]:
            item = QTreeWidgetItem(self.sock_tree, [
                s.process_name,
                s.local_address,
                f"🌐 {s.remote_address}",
                s.protocol,
                s.state,
                ""
            ])
            if s.is_blocked:
                item.setText(4, "🔴 BLOCKED")
                item.setForeground(4, Qt.GlobalColor.red)
            else:
                item.setForeground(4, Qt.GlobalColor.green)

            # Block Button
            btn_act = QPushButton("🚫" if not s.is_blocked else "🔒")
            btn_act.setFixedSize(28, 24)
            btn_act.setObjectName("QuietBtn")
            btn_act.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_act.clicked.connect(lambda _, sc=s: self.block_socket_requested.emit(sc))
            self.sock_tree.setItemWidget(item, 5, btn_act)

    def retranslate(self):
        self.lbl_title.setText(i18n["trafficTitle"])
        self.lbl_sub.setText(i18n["trafficSub"])
        self.btn_1m.setText(i18n["minute"])
        self.btn_5m.setText(i18n["fiveMinutes"])
        self.btn_15m.setText(i18n["fifteenMinutes"])
        self.lbl_leg_dl.setText(f"🟢 {i18n['download']}")
        self.lbl_leg_ul.setText(f"🔵 {i18n['upload']}")
        self.lbl_sum_note.setText(i18n["connected"])
        self.lbl_sock_title.setText(i18n["activeSockets"])
        self.sock_tree.setHeaderLabels([
            i18n["process"], i18n["local"], i18n["remote"], i18n["protocol"], i18n["state"], i18n["action"]
        ])
