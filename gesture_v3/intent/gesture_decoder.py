
import time
import math
from gesture_v3 import engine_constants

class GestureClassifier:
    """
    Intent Engine.
    Uses confidence buckets to determine gesture state.
    States:
    - IDLE: No hand or ambiguous
    - MOVE: Open palm, cursor moving
    - CLICK_LEFT: Thumb + Index pinch confirmed
    - CLICK_RIGHT: Thumb + Middle pinch confirmed
    - SCROLL: Peace sign (Index + Middle up)
    - FIST: All fingers closed (drag toggle)
    - DRAG_ACTIVE: Fist toggled, holding click
    """
    def __init__(self):
        self.state = "IDLE"
        self.pinch_confidence = 0.0
        self.last_update = time.time()
        self.prev_wrist = None
        self.pinch_type = None

    def process(self, landmarks):
        """
        Analyze landmarks to determine intent.
        :param landmarks: Normalized Landmark list
        :return: (State, MetaDataDict)
        """
        if not landmarks:
            self.state = "IDLE"
            self.pinch_confidence = 0.0
            self.prev_wrist = None
            return self.state, {"confidence": 0.0}

        # 1. Calc Click Pinch (Thumb + Index)
        thumb = landmarks[4]
        index = landmarks[8]
        dist_click = math.hypot(thumb.x - index.x, thumb.y - index.y)

        # 2. Calc Right Click Pinch (Thumb + Middle)
        middle = landmarks[12]
        dist_right = math.hypot(thumb.x - middle.x, thumb.y - middle.y)

        # 3. Velocity Gate (Prevent click while moving fast)
        wrist = landmarks[0]
        curr_time = time.time()
        dt = curr_time - self.last_update
        self.last_update = curr_time

        velocity = 0.0
        if self.prev_wrist is not None:
            dx = wrist.x - self.prev_wrist.x
            dy = wrist.y - self.prev_wrist.y
            dist_move = math.hypot(dx, dy)
            if dt > 0:
                velocity = dist_move / dt

        self.prev_wrist = wrist

        # 4. Confidence Accumulation
        is_stable = velocity < engine_constants.VELOCITY_GATE_THRESHOLD

        if dist_click < engine_constants.PINCH_THRESHOLD_NORM and is_stable:
            self.pinch_confidence += engine_constants.CONFIDENCE_GROWTH
            self.pinch_type = "LEFT"
        elif dist_right < engine_constants.PINCH_THRESHOLD_NORM and is_stable:
            self.pinch_confidence += engine_constants.CONFIDENCE_GROWTH
            self.pinch_type = "RIGHT"
        else:
            self.pinch_confidence -= engine_constants.CONFIDENCE_DECAY

        self.pinch_confidence = max(0.0, min(1.0, self.pinch_confidence))

        # --- GESTURE CLASSIFICATION ---

        # 1. Basic Finger States (Up/Down)
        fingers_up = [False] * 5

        # Index (8), Middle (12), Ring (16), Pinky (20) — compare Tip Y to PIP Y
        for i, tip_idx in enumerate([8, 12, 16, 20]):
            pip_idx = tip_idx - 2
            fingers_up[i + 1] = landmarks[tip_idx].y < landmarks[pip_idx].y

        # Thumb (4): distance to index MCP(5) determines if extended
        thumb_tip = landmarks[4]
        index_mcp = landmarks[5]
        thumb_out = math.hypot(thumb_tip.x - index_mcp.x, thumb_tip.y - index_mcp.y) > engine_constants.THUMB_OUT_DISTANCE
        fingers_up[0] = thumb_out

        # 2. Key Gestures
        is_fist = not any(fingers_up[1:])
        is_palm = all(fingers_up)
        is_peace = fingers_up[1] and fingers_up[2] and not fingers_up[3] and not fingers_up[4]

        # Pinches
        dist_index = math.hypot(landmarks[4].x - landmarks[8].x, landmarks[4].y - landmarks[8].y)
        is_pinch_index = dist_index < engine_constants.PINCH_THRESHOLD_NORM

        dist_middle = math.hypot(landmarks[4].x - landmarks[12].x, landmarks[4].y - landmarks[12].y)
        is_pinch_middle = dist_middle < engine_constants.PINCH_THRESHOLD_NORM

        # 3. State Determination — Priority: PINCH > SCROLL > FIST > PALM > IDLE
        if is_pinch_index and self.pinch_confidence >= engine_constants.GESTURE_CONFIDENCE_THRESHOLD:
            self.state = "CLICK_LEFT"
        elif is_pinch_middle and self.pinch_confidence >= engine_constants.GESTURE_CONFIDENCE_THRESHOLD:
            self.state = "CLICK_RIGHT"
        elif is_peace:
            self.state = "SCROLL"
        elif is_fist:
            self.state = "FIST"
        elif is_palm:
            self.state = "MOVE"
        else:
            self.state = "IDLE"

        return self.state, {
            "confidence": self.pinch_confidence,
            "pinch_dist": dist_index
        }
