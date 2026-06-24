"""Detection package - CV-based signal extraction from webcam frames."""

from src.detection.expression import Expression, ExpressionClassifier
from src.detection.face_mesh import FaceMeshDetector
from src.detection.gaze_classifier import GazeState, classify_gaze
from src.detection.head_pose import estimate_head_pose
from src.detection.object_detector import ObjectDetector
from src.detection.drowsiness import DrowsinessDetector, compute_ear
from src.detection.yawn import YawnDetector, compute_mar

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
