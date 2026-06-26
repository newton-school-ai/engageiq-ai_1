"""MediaPipe Face Mesh integration for 468-landmark face detection."""

import numpy as np


class FaceMeshDetector:
    """Detects 468 facial landmarks using MediaPipe Face Mesh."""

    def __init__(self, max_faces: int = 1, min_detection_confidence: float = 0.5):
        self.max_faces = max_faces
        self.min_detection_confidence = min_detection_confidence
        self._mesh = None  # Lazy init

    def _init_mesh(self):
        """Initialize MediaPipe Face Mesh (lazy to avoid import on module load)."""
        import mediapipe as mp

        self._mesh = mp.solutions.face_mesh.FaceMesh(
            max_num_faces=self.max_faces,
            min_detection_confidence=self.min_detection_confidence,
            min_tracking_confidence=0.5,
        )

    def detect(self, frame: np.ndarray) -> list | None:
        """Detect face landmarks in a frame.

        Args:
            frame: BGR image as numpy array.

        Returns:
            List of 468 (x, y, z) landmark tuples, or None if no face detected.
        """
        # TODO: Implement detection
        raise NotImplementedError

    def close(self):
        """Release MediaPipe resources."""
        if self._mesh:
            self._mesh.close()


if __name__ == "__main__":
    print("Run: python -m src.detection.face_mesh --demo")
