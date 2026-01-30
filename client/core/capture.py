from __future__ import annotations
from typing import Dict, Tuple
import mss

def grab_region(region: Dict[str, int]) -> Tuple[bytes, int, int]:
    monitor = {
        "left": region["x"],
        "top": region["y"],
        "width": region["w"],
        "height": region["h"],
    }

    try:
        with mss.mss() as sct:
            shot = sct.grab(monitor)
            return shot.raw, shot.width, shot.height
            print: ("capture succeed")
    except Exception as e:
        raise RuntimeError(f"Capture failed: {e}")
