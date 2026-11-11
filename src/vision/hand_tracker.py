from pathlib import Path
import cv2
import mediapipe as mp
from .landmarks import HandObservation

class HandTracker:
    """MediaPipe Tasks hand tracker. Requires assets/hand_landmarker.task."""
    def __init__(self, model_path: Path, confidence: float = .55):
        if not model_path.is_file():
            raise FileNotFoundError(f"Hand model not found: {model_path}. See README for setup.")
        from mediapipe.tasks import python
        from mediapipe.tasks.python import vision
        options = vision.HandLandmarkerOptions(
            base_options=python.BaseOptions(model_asset_path=str(model_path)),
            running_mode=vision.RunningMode.VIDEO, num_hands=1,
            min_hand_detection_confidence=confidence,
            min_hand_presence_confidence=confidence,
            min_tracking_confidence=confidence)
        self._tracker = vision.HandLandmarker.create_from_options(options)
        self._mp = mp

    def process(self, frame, timestamp_ms):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = self._mp.Image(image_format=self._mp.ImageFormat.SRGB, data=rgb)
        result = self._tracker.detect_for_video(image, timestamp_ms)
        observations = []
        for i, points in enumerate(result.hand_landmarks):
            coords = tuple((p.x, p.y, p.z) for p in points)
            category = result.handedness[i][0] if i < len(result.handedness) and result.handedness[i] else None
            observations.append(HandObservation(coords, category.score if category else 1.0, category.category_name if category else "Unknown"))
        return observations

    def close(self): self._tracker.close()
