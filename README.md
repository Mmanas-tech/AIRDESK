# AirDesk

Real-time hand gesture recognition system that turns your webcam into a contactless input device. MediaPipe extracts hand landmarks, an ML model classifies gestures, and pyautogui executes desktop actions — all over a WebSocket connection with a cyberpunk HUD frontend.

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white)
![React](https://img.shields.io/badge/React-18-61DAFB?logo=react&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?logo=fastapi&logoColor=white)
![MediaPipe](https://img.shields.io/badge/MediaPipe-0.10-FF6F00)
![XGBoost](https://img.shields.io/badge/XGBoost-2.0-E2231A?logo=xgboost&logoColor=white)

---

## How It Works

```
Webcam → React (capture frame via WebSocket) → FastAPI backend
    → MediaPipe Hands (21 landmarks × 3 coords = 63 features)
    → XGBoost classifier (99.91% accuracy)
    → pyautogui (executes mapped desktop action)
    → Result streamed back to frontend HUD
```

1. **Frontend** captures webcam frames and sends them over a WebSocket
2. **Backend** runs MediaPipe hand detection, extracts 21 landmarks (63-dim vector)
3. **XGBoost** model classifies the gesture in <1ms
4. **Action executor** maps gestures to desktop actions (scroll, click, volume, mouse movement)
5. **HUD overlay** displays real-time gesture, confidence, landmarks, and action log

## Gesture Mapping

| Gesture | Image | Action |
|---------|-------|--------|
| `01_palm` | Open palm | Scroll up |
| `02_l` | L-shape | Move mouse up |
| `03_fist` | Closed fist | Scroll down |
| `04_fist_moved` | Fist move | Right click |
| `05_thumb` | Thumb up | Volume up |
| `06_index` | Point | Move mouse left |
| `07_ok` | OK sign | Left click |
| `08_palm_moved` | Palm move | Scroll down |
| `09_c` | C-shape | Play/pause |
| `10_down` | Point down | Move mouse down |

## Project Structure

```
AirDesk/
├── backend/                 # FastAPI + WebSocket server
│   ├── main.py              # FastAPI app, REST endpoints, static mount
│   ├── config.py            # All configuration constants
│   ├── websocket_handler.py # WebSocket frame processing loop
│   ├── gesture_pipeline.py  # Orchestrator: detect → extract → classify → act
│   ├── hand_tracker.py      # MediaPipe Hands wrapper
│   ├── feature_extractor.py # Landmark → 63-dim feature vector
│   ├── model_manager.py     # Sklearn model loader (RF, XGBoost)
│   ├── model_manager_torch.py # PyTorch model loader (MLP, LSTM)
│   ├── action_executor.py   # pyautogui action dispatcher
│   └── db.py                # SQLite gesture/action logging
│
├── frontend/                # React + TypeScript + Tailwind
│   ├── src/
│   │   ├── App.tsx          # Main layout with HUD panels
│   │   ├── components/      # 10 UI components
│   │   │   ├── WebcamFeed.tsx
│   │   │   ├── GestureDisplay.tsx
│   │   │   ├── ConfidenceBar.tsx
│   │   │   ├── LandmarkOverlay.tsx
│   │   │   ├── GestureConfigPanel.tsx
│   │   │   ├── ModelSelector.tsx
│   │   │   ├── StatsPanel.tsx
│   │   │   ├── LogFeed.tsx
│   │   │   ├── ConnectionStatus.tsx
│   │   │   └── CornerBracket.tsx
│   │   ├── hooks/           # useWebSocket, useWebcam, useGestureHistory
│   │   ├── utils/           # frameCapture, drawLandmarks, api
│   │   ├── types/           # TypeScript interfaces
│   │   └── constants/       # Gesture names, colors, action labels
│   ├── vite.config.ts       # Proxy /ws → localhost:8000
│   └── tailwind.config.ts
│
├── training/                # ML training pipeline
│   ├── dataset_loader.py    # LeapGestRecog, HaGRID, custom CSV loaders
│   ├── augment.py           # 5 augmentation types (scale, translate, rotate, mirror, noise)
│   ├── preprocess.py        # Landmark normalization + sklearn scaler
│   ├── train.py             # Full CLI: RF, XGBoost, MLP, LSTM
│   ├── evaluate.py          # Metrics, confusion matrix, per-class report
│   └── export_model.py      # Export + update backend config
│
├── scripts/                 # Utility scripts
│   ├── setup_and_train.py   # One-command: verify → download → train → evaluate
│   ├── download_dataset.py  # Kaggle LeapGestRecog download
│   ├── collect_custom_gestures.py # Record custom gestures via webcam
│   ├── verify_installation.py     # Pre-flight check
│   └── test_pipeline.py     # End-to-end smoke test
│
├── models/                  # Trained model files (.pkl, .pt)
├── datasets/                # Downloaded datasets
├── backend/requirements.txt
├── requirements_training.txt
└── .gitignore
```

## Quick Start

### 1. Clone & Install

```bash
git clone https://github.com/yourusername/AirDesk.git
cd AirDesk

# Backend + inference dependencies
pip install -r backend/requirements.txt

# Frontend
cd frontend && npm install && cd ..
```

### 2. Train the Model

```bash
# One-command pipeline: downloads dataset, trains XGBoost, evaluates
python scripts/setup_and_train.py

# Or step-by-step:
python scripts/download_dataset.py
python -m training.train --model xgb --dataset leap --leap-path datasets/leapGestRecog
python -m training.evaluate --model models/xgboost_*.pkl --dataset leap --leap-path datasets/leapGestRecog
```

This trains an XGBoost classifier on the [LeapGestRecog](https://www.kaggle.com/datasets/gti-upm/leapgestrecog) dataset (~20K images, 10 gesture classes). The model achieves **99.91% accuracy** with ~6s training time on CPU.

### 3. Run

```bash
# Terminal 1 — Backend
uvicorn backend.main:app --host 0.0.0.0 --port 8000

# Terminal 2 — Frontend
cd frontend && npm run dev
```

Open **http://localhost:5173** in your browser.

## Training Options

```bash
python -m training.train --help

# Model types
python -m training.train --model rf    # Random Forest (with GridSearchCV)
python -m training.train --model xgb   # XGBoost (recommended, 99.91% acc)
python -m training.train --model mlp   # PyTorch MLP (256→128→C)
python -m training.train --model lstm  # PyTorch LSTM (2-layer, 128 hidden)

# Dataset options
--dataset leap          # LeapGestRecog only
--dataset hagrid        # HaGRID only
--dataset both          # Combined
--dataset custom --custom-path <dir>  # Custom CSV folder

# Training options
--augment               # Enable data augmentation
--augment-factor 3      # Augmentation multiplier
--epochs 100            # For MLP/LSTM
--tune                  # GridSearchCV for RF
```

## Configuration

Edit `backend/config.py` to adjust:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `MODEL_PATH` | `models/xgboost_*.pkl` | Path to trained model |
| `MODEL_TYPE` | `xgboost` | `random_forest`, `xgboost`, `mlp`, `lstm` |
| `CONFIDENCE_THRESHOLD` | `0.75` | Min confidence to trigger action |
| `FRAME_SKIP_RATE` | `2` | Process every Nth frame |
| `ACTION_COOLDOWN_MS` | `500` | Min ms between repeated actions |
| `GESTURE_SMOOTHING_WINDOW` | `5` | Rolling window for stable predictions |
| `MOUSE_STEP` | `50` | Pixels per mouse movement |

## Custom Gestures

Record your own gestures with the built-in collector:

```bash
python scripts/collect_custom_gestures.py
```

This opens your webcam, lets you record 100 frames per gesture, and saves them as CSV files in `datasets/custom/`. Then train on your custom data:

```bash
python -m training.train --model xgb --dataset custom --custom-path datasets/custom
```

## Tech Stack

- **Hand Detection**: MediaPipe Hands (0.10.x) — 21 landmarks, 3D coordinates
- **Classification**: XGBoost 2.0 — gradient boosted trees, CPU-optimized
- **Backend**: FastAPI + WebSocket (uvicorn)
- **Frontend**: React 18 + TypeScript + Tailwind CSS + Vite
- **Desktop Control**: pyautogui (mouse, keyboard, scroll)
- **Database**: SQLite via aiosqlite (gesture/action logging)

## License

MIT
