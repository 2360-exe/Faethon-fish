# client/ui/app_qt.py
from client.ui.widgets.preview_widget import PreviewWidget

import os
from client.ui.region_select_qt import RegionSelectOverlay
from client.config.config_io import load_config, save_config, set_capture_region
from PySide6.QtCore import Qt
from PySide6.QtGui import QMovie, QGuiApplication
from PySide6.QtWidgets import (
    QLabel, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QFrame, QApplication, QComboBox, QCheckBox
)

from client.ui.theme_qt import THEME_QSS


def _asset_path(*parts: str) -> str:
    here = os.path.dirname(os.path.abspath(__file__))
    client_dir = os.path.dirname(here)
    return os.path.join(client_dir, "assets", *parts)


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Autofisher // POC")
        self.setMinimumSize(780, 520)

        self.cfg = load_config()
        self.runner = None
        self.is_running = False

        root = QWidget()
        self.setCentralWidget(root)
        main = QVBoxLayout(root)
        main.setContentsMargins(12, 12, 12, 12)
        main.setSpacing(10)

        # --- Blinker header ---
        self.blinker_label = QLabel()
        self.blinker_label.setAlignment(Qt.AlignCenter)
        self.blinker_label.setFixedHeight(90)
        self.blinker_label.setScaledContents(True)

        gif_path = _asset_path("blinker.gif")
        if os.path.exists(gif_path):
            self.movie = QMovie(gif_path)
            self.blinker_label.setMovie(self.movie)
            self.movie.start()
        else:
            self.movie = None
            self.blinker_label.setText("BLINKER GIF MISSING")

        main.addWidget(self.blinker_label)

        # --- Title / status bar ---
        top = QHBoxLayout()
        self.title = QLabel("AUTOFISHER // POC")
        self.title.setObjectName("TitleLabel")

        self.status = QLabel("STATE: IDLE")
        self.status.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        top.addWidget(self.title, 1)
        top.addWidget(self.status, 1)
        main.addLayout(top)

        # --- Panels ---
        body = QHBoxLayout()
        body.setSpacing(10)

        left = self._panel()
        right = self._panel()

        body.addWidget(left, 1)
        body.addWidget(right, 2)
        main.addLayout(body, 1)

        # Left content
        left_layout = left.layout()

        left_layout.addWidget(QLabel("MONITOR:"))
        self.monitor_combo = QComboBox()

        screens = QGuiApplication.screens()
        for i, s in enumerate(screens):
            g = s.geometry()
            self.monitor_combo.addItem(
                f"Monitor {i+1}: {g.width()}x{g.height()} @ ({g.x()},{g.y()})",
                userData=i,
            )

        mon_idx = int(self.cfg.get("capture", {}).get("monitor_index", 0))
        mon_idx = max(0, min(mon_idx, self.monitor_combo.count() - 1))
        self.monitor_combo.setCurrentIndex(mon_idx)
        left_layout.addWidget(self.monitor_combo)

        self.region_label = QLabel(self._region_text())
        left_layout.addWidget(QLabel("CAPTURE REGION:"))
        left_layout.addWidget(self.region_label)

        btn_row = QHBoxLayout()
        self.btn_calibrate = QPushButton("CALIBRATE")
        self.btn_start = QPushButton("START")
        self.btn_stop = QPushButton("STOP")
        self.btn_stop.setEnabled(False)

        btn_row.addWidget(self.btn_calibrate)
        btn_row.addWidget(self.btn_start)
        btn_row.addWidget(self.btn_stop)
        left_layout.addLayout(btn_row)

        self.btn_start.clicked.connect(self.on_start)
        self.btn_stop.clicked.connect(self.on_stop)
        self.btn_calibrate.clicked.connect(self.on_calibrate)

        # Right content
        right_layout = right.layout()
        right_layout.addWidget(QLabel("LIVE FEED:"))

        self.cb_zone = QCheckBox("Show zone")
        self.cb_bar = QCheckBox("Show bar")
        self.cb_nums = QCheckBox("Show numbers")

        self.cb_zone.setChecked(True)
        self.cb_bar.setChecked(True)
        self.cb_nums.setChecked(True)

        toggles_row = QHBoxLayout()
        toggles_row.addWidget(self.cb_zone)
        toggles_row.addWidget(self.cb_bar)
        toggles_row.addWidget(self.cb_nums)
        toggles_row.addStretch(1)
        right_layout.addLayout(toggles_row)

        self.preview = PreviewWidget()
        right_layout.addWidget(self.preview, 1)

        # Wire toggles (no-op for now; overlay always on)
        for cb in (self.cb_zone, self.cb_bar, self.cb_nums):
            cb.stateChanged.connect(self._apply_overlay_flags)

        self._apply_overlay_flags()
        self._refresh()

    def _panel(self) -> QFrame:
        panel = QFrame()
        panel.setObjectName("Panel")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)
        return panel

    def _region_text(self) -> str:
        region = self.cfg.get("capture", {}).get("region")
        if not region:
            return "NOT SET"
        return f'x={region["x"]}, y={region["y"]}, w={region["w"]}, h={region["h"]}'

    def _apply_overlay_flags(self):
        # New PreviewWidget always shows overlay; toggles are currently cosmetic.
        # You can later wire these to enable/disable drawing if you want.
        pass

    def _refresh(self):
        self.cfg = load_config()
        self.region_label.setText(self._region_text())

        has_region = bool(self.cfg.get("capture", {}).get("region"))

        self.btn_start.setEnabled(has_region and not self.is_running)
        self.btn_stop.setEnabled(self.is_running)

        if not has_region and not self.is_running:
            self.status.setText("STATE: NO REGION")

    def on_calibrate(self):
        mon_idx = int(self.monitor_combo.currentData())
        cfg = load_config()
        cfg["capture"]["monitor_index"] = mon_idx
        save_config(cfg)

        screens = QGuiApplication.screens()
        mon_idx = max(0, min(mon_idx, len(screens) - 1))
        screen = screens[mon_idx]

        self.status.setText("STATE: CALIBRATING")

        def _done(x, y, w, h):
            set_capture_region(x, y, w, h)
            self.status.setText("STATE: IDLE")
            self._refresh()

        self._overlay = RegionSelectOverlay(screen, on_selected=_done)
        self._overlay.show()
        self._overlay.raise_()
        self._overlay.activateWindow()

    def on_start(self):
        print("START CLICKED")

        self.cfg = load_config()
        region = self.cfg["capture"]["region"]

        from client.core.runner import Runner
        self.runner = Runner(region)

        self.runner.frame_ready.connect(self.preview.update_frame)

        # Stop preview timer (runner will push frames)
        self.preview.timer.stop()

        self.runner.start()

        self.is_running = True
        self.status.setText("STATE: RUNNING")
        self._refresh()

    def on_stop(self):
        if self.runner:
            try:
                # New Controller API: reset() instead of force_release()
                self.runner.controller.reset()
            except Exception:
                pass

            self.runner.stop()
            self.runner = None

        # Restart preview timer
        self.preview.timer.start()

        self.is_running = False
        self.status.setText("STATE: IDLE")
        self._refresh()


def run():
    import sys
    app = QApplication(sys.argv)
    app.setStyleSheet(THEME_QSS)

    win = MainWindow()
    win.move(100, 100)
    win.show()
    win.raise_()
    win.activateWindow()

    sys.exit(app.exec())
