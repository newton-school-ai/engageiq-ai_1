"""Detection package - CV-based signal extraction from webcam frames."""

from src.detection.drowsiness import DrowsinessDetector, compute_ear  # noqa: F401
from src.detection.expression import Expression, ExpressionClassifier  # noqa: F401
from src.detection.face_mesh import FaceMeshDetector  # noqa: F401
from src.detection.gaze_classifier import GazeState, classify_gaze  # noqa: F401
from src.detection.head_pose import estimate_head_pose  # noqa: F401
from src.detection.object_detector import ObjectDetector  # noqa: F401
from src.detection.yawn import YawnDetector, compute_mar  # noqa: F401

__all__ = [
    "Expression",
    "ExpressionClassifier",
    "FaceMeshDetector",
    "GazeState",
    "classify_gaze",
    "estimate_head_pose",
    "ObjectDetector",
    "DrowsinessDetector",
    "compute_ear",
    "YawnDetector",
    "compute_mar",
]
