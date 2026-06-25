"""EAR-based drowsiness detection with temporal smoothing."""


def compute_ear(eye_landmarks: list[tuple[float, float]]) -> float:
    """Compute Eye Aspect Ratio from 6 eye landmarks.

    Args:
        eye_landmarks: List of 6 (x, y) tuples representing eye contour points.

    Returns:
        EAR value as float. Below 0.25 indicates closed eye.
    """
    # TODO: Implement EAR computation
    raise NotImplementedError


class DrowsinessDetector:
    """Detects drowsiness from sustained eye closure."""

    def __init__(self, ear_threshold: float = 0.25, drowsy_duration: float = 1.5):
        self.ear_threshold = ear_threshold
        self.drowsy_duration = drowsy_duration
        self._closed_start = None

    def update(self, ear: float, timestamp: float) -> bool:
        """Update detector with new EAR reading.

        Args:
            ear: Current Eye Aspect Ratio.
            timestamp: Current time in seconds.

        Returns:
            True if drowsiness detected (sustained closure > threshold duration).
        """
        # TODO: Implement temporal tracking
        raise NotImplementedError
