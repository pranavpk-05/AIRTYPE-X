from dataclasses import dataclass
from pathlib import Path
import sys

ROOT = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parents[2]))
MODEL_PATH = ROOT / "assets" / "hand_landmarker.task"

@dataclass
class Settings:
    camera_index: int = 0
    simulation: bool = True
    real_control: bool = False
    sensitivity: float = 1.0
    smoothing: float = 0.35
    pinch_on: float = 0.045
    pinch_off: float = 0.065
    confidence: float = 0.55
    scroll_sensitivity: float = 1.0
    keyboard_scale: float = 1.0

    double_click_time: float = .35
    drag_time: float = .5
    right_click_enabled: bool = False
    region_margin: float = 0.0
