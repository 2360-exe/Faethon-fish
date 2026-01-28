''' OLD CODE!!!!
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
'''

from __future__ import annotations

import time
from typing import Any, Dict

from PySide6.QtCore import QThread, Signal

from .capture import grab_region
from .vision_simple import detect_zone_and_bar_bgra, DetectionResult
from .controller import Controller


class Runner(QThread):
    # use object to avoid typing issues
    frame_ready = Signal(object, int, int, object)

    def __init__(self, region: Dict[str, int], parent: Any = None) -> None:
        super().__init__(parent)
        self.region = region
        self.controller = Controller()  
        self.running = False

    def start(self, priority=QThread.InheritPriority) -> None:
        self.running = True
        super().start(priority)

    def stop(self) -> None:
        self.running = False
        # Make sure reset is safe to call from the thread that calls stop (main thread)
        try:
            self.controller.reset()
        except Exception as e:
            print("Controller reset error:", e)
        self.wait(2000)  # optional timeout

    def run(self) -> None:
        while self.running:
            try:
                raw, w, h = grab_region(self.region)
                result: DetectionResult = detect_zone_and_bar_bgra(raw, w, h)

                # DON'T call controller.update() from this thread if controller touches Qt
                # Option 1: shows result and lets a main-thread slot call controller.update
                self.frame_ready.emit(raw, w, h, result)

                # self.controller.update(result). also option 2: if controller is thread-safe

            except Exception as e:
                print("Runner error:", e)
                # decide whether to stop or continue; here we continue after a short pause
                time.sleep(0.05)
                continue

            # sleep a small amount to limit cpu usage 
            QThread.msleep(10)
