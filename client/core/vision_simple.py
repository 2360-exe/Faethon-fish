from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
import numpy as np


@dataclass
class DetectionResult:
    white_y: Optional[int]
    bar_y: Optional[int]
    distance: Optional[float]
    active: bool


def detect_zone_and_bar_bgra(raw: bytes, w: int, h: int) -> DetectionResult:
  

    if not raw or w <= 0 or h <= 0:
        return DetectionResult(None, None, None, False)

    # Convert BGRA → (h, w, 4)
    arr = np.frombuffer(raw, dtype=np.uint8)
    try:
        arr = arr.reshape((h, w, 4))
    except ValueError:
        return DetectionResult(None, None, None, False)

    # Convert to brightness
    rgb = arr[..., :3]
    brightness = rgb.sum(axis=2)

  
    
    # edit as needed until working - faye in class
    CROP_LEFT = int(w * 0.40)
    CROP_RIGHT = int(w * 0.60)

    cropped = brightness[:, CROP_LEFT:CROP_RIGHT]

    # edit thresholds as needed
    white_mask = cropped > 650
    black_mask = cropped < 100

    white_counts = white_mask.sum(axis=1)
    black_counts = black_mask.sum(axis=1)

    # Require minimal signal
    if white_counts.max() < 2 or black_counts.max() < 2:
        return DetectionResult(None, None, None, False)

    white_y = int(np.argmax(white_counts))
    bar_y = int(np.argmax(black_counts))

    distance = float(white_y - bar_y)
    return DetectionResult(white_y, bar_y, distance, True)
