
"""
Centralized source of truth for all physics, UI, and logic constants.
"""
from enum import Enum

# --- GESTURE STATES ---
class GestureState(str, Enum):
    IDLE = "IDLE"
    MOVE = "MOVE"
    CLICK_LEFT = "CLICK_LEFT"
    CLICK_RIGHT = "CLICK_RIGHT"
    SCROLL = "SCROLL"
    FIST = "FIST"
    DRAG_ACTIVE = "DRAG_ACTIVE"

# --- SYSTEM ---
APP_NAME = "AIRDESK"
TARGET_FPS = 60

# --- CAMERA ---
CAMERA_INDEX = 0
FRAME_WIDTH = 1280
FRAME_HEIGHT = 720

def get_screen_size():
    """Query screen size at runtime (avoids crash in headless/SSH)."""
    import pyautogui
    return pyautogui.size()

# --- PERCEPTION (OneEuroFilter) ---
ONE_EURO_MIN_CUTOFF = 0.5   # Hz. Lower = more smoothing when slow
ONE_EURO_BETA = 4.0         # Speed coefficient for adaptive cutoff
ONE_EURO_D_CUTOFF = 1.0     # Hz. Cutoff for derivative

# --- GESTURE CONFIG ---
GESTURE_CONFIDENCE_THRESHOLD = 0.8
CONFIDENCE_DECAY = 0.2
CONFIDENCE_GROWTH = 0.15
PINCH_THRESHOLD_NORM = 0.06
VELOCITY_GATE_THRESHOLD = 2.0  # Max hand speed to allow click
THUMB_OUT_DISTANCE = 0.05      # Min distance for thumb to be "extended"

# --- V6 RELATIVE PHYSICS (AIR MOUSE) ---
DEAD_ZONE = 0.002
BASE_SENSITIVITY = 3.0
ACCELERATION_FACTOR = 20.0
MAX_SENSITIVITY = 12.0
DELTA_SMOOTHING = 0.6

# --- GESTURES ---
CLICK_COOLDOWN = 0.4

# Scroll
SCROLL_SPEED = 20
SCROLL_DEADZONE = 0.005

# Drag (Toggle)
DRAG_TOGGLE_COOLDOWN = 1.0
COLOR_DRAG_ACTIVE = (0, 255, 0)

# --- UI COLORS (BGR) ---
COLOR_IDLE = (255, 255, 0)
COLOR_MOVE = (255, 255, 255)
COLOR_CLICK = (0, 0, 255)
COLOR_RIGHT_CLICK = (255, 0, 0)
COLOR_SCROLL = (255, 0, 255)
COLOR_TEXT = (255, 255, 255)

# --- SAFETY ---
FAILSAFE_FPS = 15
