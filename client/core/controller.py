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

        # You can tune threshold and cooldown to fit the game's responsiveness!!!
        # tuning
        self.min_hold = 0.002      # smallest possible hold
        self.max_hold = 0.018      # gentle max hold
        self.cooldown = 0.0015     # rate limit for toggles
        self.threshold = 2         # pixels of current and past inputs before toggling hold state

        self.last_action = time.monotonic()
        self.holding = False       # whether we currently have the left mouse held down

    def reset(self) -> None:
        if self.holding:
            pyautogui.mouseUp(button="left")
            self.holding = False
        else:
            pyautogui.mouseUp(button="left")

    def update(self, result: Optional[DetectionResult]) -> None:
        # If detection lost or inactive, makes sure we release
        if not result or not result.active or result.distance is None:
            if self.holding:
                pyautogui.mouseUp(button="left")
                self.holding = False
                self.last_action = time.monotonic()
            return

        d = result.distance  # white_y - bar_y 
        now = time.monotonic()

        # rate limit toggles
        if now - self.last_action < self.cooldown:
            return

        
        if d < -self.threshold:
            # bar ABOVE white - lower - RELEASE if currently holding
            if self.holding:
                pyautogui.mouseUp(button="left")
                self.holding = False
                self.last_action = now
            return

        if d > self.threshold:
            # bar BELOW white, RAISE, HOLD if not already holding
            if not self.holding:
                # move cursor to the detected bar position before holding.
                # helps if the cursor isn't already over the bar
                # only does this if the DetectionResult supplies coordinates.
                if hasattr(result, "bar_x") and hasattr(result, "bar_y"):
                    try:
                        # move instantly to the bar position 
                        pyautogui.moveTo(result.bar_x, result.bar_y, duration=0)
                    except Exception:
                        # ignore move failures 
                        pass

                pyautogui.mouseDown(button="left")
                self.holding = True
                self.last_action = now
            return

        # If within the threshold band, do nothing (keep current hold state)
        return
'''
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
        '''

