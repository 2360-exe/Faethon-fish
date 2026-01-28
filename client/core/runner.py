from __future__ import annotations

import time
from typing import Any, Dict

from PySide6.QtCore import QThread, Signal

from .capture import grab_region
from .vision_simple import detect_zone_and_bar_bgra, DetectionResult
from .controller import Controller


class Runner(QThread):
    frame_ready = Signal(bytes, int, int, object)

    def __init__(self, region: Dict[str, int], parent: Any = None) -> None:
        super().__init__(parent)
        self.region = region
        self.controller = Controller()
        self.running = False

    def start(self) -> None:
        self.running = True
        super().start()

    def stop(self) -> None:
        self.running = False
        self.controller.reset()
        self.wait()

    def run(self) -> None:
        while self.running:
            try:
                raw, w, h = grab_region(self.region)
            except Exception as e:
                print("Runner capture error:", e)
                time.sleep(0.05)
                continue

            result: DetectionResult = detect_zone_and_bar_bgra(raw, w, h)
            self.controller.update(result)

            self.frame_ready.emit(raw, w, h, result)
            time.sleep(0.01)
