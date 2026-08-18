# AIRDESK

A real-time hand gesture PC control system using your webcam. Control your mouse cursor, perform clicks, scroll, and drag — all with hand gestures.

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white)
![MediaPipe](https://img.shields.io/badge/MediaPipe-0.10-FF6F00)
![OpenCV](https://img.shields.io/badge/OpenCV-4.10-5C3EE8?logo=opencv&logoColor=white)
![pyautogui](https://img.shields.io/badge/pyautogui-0.9-4CAF50)

---

## How It Works

```
Webcam → MediaPipe Hand Landmarker (21 landmarks)
  → OneEuroFilter (jitter smoothing)
  → GestureDecoder (intent classification)
  → PhysicsCursor (relative air-mouse movement)
  → pyautogui (desktop actions)
  → CinematicHUD (real-time overlay)
```

## Gesture Controls

| Gesture | Action |
|---------|--------|
| **Open Palm** (all fingers up) | Move cursor |
| **Thumb + Index Pinch** | Left click |
| **Thumb + Middle Pinch** | Right click |
| **Peace Sign** (Index + Middle up) | Scroll mode |
| **Closed Fist** | Toggle drag mode |
| **Press Q** | Quit |

## Project Structure

```
AIRDESK/
├── app_launcher.py                    # Entry point
├── settings.py                        # Legacy V1/V2 configuration
├── ml_hand_model.task                 # MediaPipe hand landmark model
├── dependencies.txt                   # Python packages
├── README.md                          # This file
├── PROJECT_OVERVIEW.md                # Legacy V1/V2 documentation
│
├── gesture_v3/                        # Core engine (V3)
│   ├── engine_constants.py            # Physics, UI, and logic constants
│   ├── core/
│   │   └── orchestrator.py            # Main system loop
│   ├── perception/
│   │   ├── landmark_detector.py       # MediaPipe wrapper
│   │   └── jitter_filter.py           # OneEuro adaptive filter
│   ├── intent/
│   │   └── gesture_decoder.py         # Confidence-based gesture classifier
│   ├── control/
│   │   └── cursor_engine.py           # Physics-based air mouse
│   └── ui/
│       └── holographic_overlay.py     # Iron Man style HUD
│
├── legacy_hand_tracker.py             # V1/V2 hand tracking (deprecated)
├── legacy_mouse_driver.py             # V1/V2 mouse control (deprecated)
└── legacy_gesture_detector.py         # V1/V2 gesture recognition (deprecated)
```

## Quick Start

### 1. Install Dependencies

```bash
pip install -r dependencies.txt
```

Requires: `opencv-python`, `mediapipe`, `numpy`, `pyautogui`

### 2. Run

```bash
python app_launcher.py
```

A camera window opens with a holographic HUD overlay. Use hand gestures to control your PC.

### 3. Quit

Press **Q** on your keyboard.

## Architecture

| Module | Purpose |
|--------|---------|
| `core/orchestrator.py` | Main loop: camera → track → classify → act → render |
| `perception/landmark_detector.py` | MediaPipe Hand Landmarker wrapper (VIDEO mode) |
| `perception/jitter_filter.py` | OneEuroFilter — adaptive low-pass for jitter reduction |
| `intent/gesture_decoder.py` | Confidence buckets for click, scroll, fist, move |
| `control/cursor_engine.py` | Relative air mouse with dead zone, acceleration, smoothing |
| `ui/holographic_overlay.py` | Reticle, finger trails, status labels |

## Configuration

Edit `gesture_v3/engine_constants.py` to adjust:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `ONE_EURO_MIN_CUTOFF` | `0.5` | Smoothing strength (lower = smoother) |
| `ONE_EURO_BETA` | `4.0` | Speed responsiveness |
| `DEAD_ZONE` | `0.002` | Minimum movement to register |
| `BASE_SENSITIVITY` | `3.0` | Cursor speed |
| `ACCELERATION_FACTOR` | `20.0` | Fast-movement gain |
| `PINCH_THRESHOLD_NORM` | `0.06` | Click detection distance |
| `CLICK_COOLDOWN` | `0.4` | Seconds between clicks |
| `SCROLL_SPEED` | `20` | Scroll sensitivity |

## License

MIT
