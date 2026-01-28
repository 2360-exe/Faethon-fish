from __future__ import annotations
from typing import Optional
import pyautogui
import time

from .vision_simple import DetectionResult


class Controller:
    """
    No-deadzone continuous controller:
    - Always applies some correction
    - Uses extremely small micro-holds
    - Very fast update rate
    - Tracks the white line closely without overshoot
    """

    def __init__(self) -> None:
        pyautogui.PAUSE = 0

        # tuning
        self.min_hold = 0.002      # smallest possible hold
        self.max_hold = 0.018      # gentle max hold
        self.cooldown = 0.0015     # very fast update rate

        self.last_action = time.monotonic()

    def reset(self) -> None:
        pyautogui.mouseUp()

    def update(self, result: Optional[DetectionResult]) -> None:
        if not result or not result.active or result.distance is None:
            pyautogui.mouseUp()
            return

        d = result.distance  # white_y - bar_y
        now = time.monotonic()

        # rate limit
        if now - self.last_action < self.cooldown:
            return

        # ---------------------------------------------------------
        # No deadzone logic:
        # If bar ABOVE white → lower
        # If bar BELOW white → raise (micro-hold)
        # ---------------------------------------------------------

        if d < 0:
            # bar ABOVE white → lower
            pyautogui.mouseUp()
            self.last_action = now
            return

        # bar BELOW white → raise with micro-hold
        # scale hold time very gently
        strength = min(1.0, d / 40.0)
        hold_time = self.min_hold + strength * (self.max_hold - self.min_hold)

        pyautogui.mouseDown()
        time.sleep(hold_time)
        pyautogui.mouseUp()

        self.last_action = now
