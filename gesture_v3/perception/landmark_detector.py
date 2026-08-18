
import mediapipe as mp
import os
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from gesture_v3 import engine_constants

class HandTracker:
    """
    Wrapper for MediaPipe Hand Landmarker.
    Uses VIDEO mode for temporal consistency (internal smoothing).
    """
    def __init__(self, model_path="ml_hand_model.task"):
        self.model_path = model_path
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"Model not found at {model_path}")

        base_options = python.BaseOptions(model_asset_path=self.model_path)

        options = vision.HandLandmarkerOptions(
            base_options=base_options,
            running_mode=vision.RunningMode.VIDEO,
            num_hands=1,
            min_hand_detection_confidence=0.5,
            min_hand_presence_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.landmarker = vision.HandLandmarker.create_from_options(options)

    def process(self, image_rgb, timestamp_ms):
        """
        Process a frame.
        :param image_rgb: OpenCV Image (RGB)
        :param timestamp_ms: Current timestamp in milliseconds (Must be increasing!)
        :return: Detection result
        """
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=image_rgb)
        result = self.landmarker.detect_for_video(mp_image, int(timestamp_ms))
        return result
