# client/config/config_io.py
from __future__ import annotations

import json
import os
from copy import deepcopy
from typing import Any, Dict, Optional


# Keep defaults in ONE place so the rest of the app never hardcodes settings.
DEFAULT_CONFIG: Dict[str, Any] = {
    "capture": {
        "region": None,  # becomes {"x": int, "y": int, "w": int, "h": int}
        "monitor_index": 0,
        "dpi_scale": 1.0,
    },
    "vision": {
        "white_threshold": 210,
        "black_threshold": 50,
        "min_blob_size": 200,
    },
    "control": {
        "tolerance_px": 12,
        "min_flip_ms": 60,
        "loop_hz": 90,
    },
    "input": {
        "mouse_button": "left",  # "left" or "right"
        "failsafe_release_on_stop": True,
    },
    "safety": {
        "stop_key": "F12",
        "require_game_focused": False,
        "max_run_seconds": 0,  # 0 = no limit
    },
    "debug": {
        "show_preview": True,
        "draw_overlay": True,
        "log_level": "info",  # "info" or "debug"
    },
}


def get_config_path() -> str:
    """
    Returns an absolute path to config.json, relative to this file location.
    This avoids issues where the working directory changes (VS Code vs double-click).
    """
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(here, "config.json")


def deep_merge(user: Dict[str, Any], defaults: Dict[str, Any]) -> Dict[str, Any]:
    """
    Recursively merges defaults into user config (user values win).
    """
    merged = deepcopy(defaults)
    for k, v in user.items():
        if isinstance(v, dict) and isinstance(merged.get(k), dict):
            merged[k] = deep_merge(v, merged[k])
        else:
            merged[k] = v
    return merged


def _is_valid_region(region: Any) -> bool:
    if not isinstance(region, dict):
        return False
    for key in ("x", "y", "w", "h"):
        if key not in region or not isinstance(region[key], int):
            return False
    if region["x"] < 0 or region["y"] < 0:
        return False
    if region["w"] <= 0 or region["h"] <= 0:
        return False
    return True


def validate_config(cfg: Dict[str, Any]) -> Dict[str, Any]:
    """
    Light validation for POC. Fixes obviously bad values.
    """
    cfg = deepcopy(cfg)

    # capture.region
    region = cfg.get("capture", {}).get("region")
    if region is not None and not _is_valid_region(region):
        cfg["capture"]["region"] = None

    # control sanity
    control = cfg.setdefault("control", {})
    tol = control.get("tolerance_px", DEFAULT_CONFIG["control"]["tolerance_px"])
    if not isinstance(tol, int) or tol < 0:
        control["tolerance_px"] = DEFAULT_CONFIG["control"]["tolerance_px"]

    min_flip = control.get("min_flip_ms", DEFAULT_CONFIG["control"]["min_flip_ms"])
    if not isinstance(min_flip, int) or min_flip < 0:
        control["min_flip_ms"] = DEFAULT_CONFIG["control"]["min_flip_ms"]

    loop_hz = control.get("loop_hz", DEFAULT_CONFIG["control"]["loop_hz"])
    if not isinstance(loop_hz, int) or not (20 <= loop_hz <= 240):
        control["loop_hz"] = DEFAULT_CONFIG["control"]["loop_hz"]

    # input sanity
    inp = cfg.setdefault("input", {})
    btn = inp.get("mouse_button", "left")
    if btn not in ("left", "right"):
        inp["mouse_button"] = "left"

    # debug sanity
    dbg = cfg.setdefault("debug", {})
    lvl = dbg.get("log_level", "info")
    if lvl not in ("info", "debug"):
        dbg["log_level"] = "info"

    return cfg


def save_config(cfg: Dict[str, Any]) -> None:
    """
    Safe write: write to temp then replace.
    """
    path = get_config_path()
    tmp_path = path + ".tmp"

    os.makedirs(os.path.dirname(path), exist_ok=True)

    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)

    # os.replace is atomic on Windows for same-volume replace
    os.replace(tmp_path, path)


def load_config() -> Dict[str, Any]:
    """
    Loads config.json. If missing, creates it from defaults.
    If corrupted, backs it up and recreates defaults.
    Always returns a validated config with missing keys filled in.
    """
    path = get_config_path()

    if not os.path.exists(path):
        cfg = deepcopy(DEFAULT_CONFIG)
        save_config(cfg)
        return cfg

    try:
        with open(path, "r", encoding="utf-8") as f:
            user_cfg = json.load(f)
        if not isinstance(user_cfg, dict):
            raise ValueError("config.json root must be an object")
    except Exception:
        # Backup broken file and recreate defaults
        bak = path + ".bak"
        try:
            if os.path.exists(bak):
                os.remove(bak)
            os.replace(path, bak)
        except Exception:
            # If backup fails, we still recreate defaults
            pass

        cfg = deepcopy(DEFAULT_CONFIG)
        save_config(cfg)
        return cfg

    merged = deep_merge(user_cfg, DEFAULT_CONFIG)
    merged = validate_config(merged)

    # If we filled in missing keys or fixed bad values, persist it.
    if merged != user_cfg:
        save_config(merged)

    return merged


def set_capture_region(x: int, y: int, w: int, h: int) -> Dict[str, Any]:
    """
    Convenience helper for calibration code.
    """
    cfg = load_config()
    cfg["capture"]["region"] = {"x": int(x), "y": int(y), "w": int(w), "h": int(h)}
    cfg = validate_config(cfg)
    save_config(cfg)
    return cfg

if __name__ == "__main__":
    print("=== CONFIG IO TEST ===")
    cfg = load_config()
    print("Loaded region:", cfg["capture"]["region"])
    print("Tolerance:", cfg["control"]["tolerance_px"])

    print("\nSetting capture region to (10, 20, 300, 500)...")
    set_capture_region(10, 20, 300, 500)

    cfg2 = load_config()
    print("Reloaded region:", cfg2["capture"]["region"])
    print("=== DONE ===")
