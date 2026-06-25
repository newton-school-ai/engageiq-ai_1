"""Head pose estimation using MediaPipe landmarks + OpenCV solvePnP."""


def estimate_head_pose(landmarks: list, frame_shape: tuple) -> tuple[float, float, float]:
    """Estimate head pose from facial landmarks.

    Args:
        landmarks: List of 468 (x, y, z) landmark tuples from FaceMeshDetector.
        frame_shape: Shape of the input frame (height, width, channels).

    Returns:
        Tuple of (pitch, yaw, roll) in degrees.
    """
    # TODO: Implement solvePnP-based pose estimation
    raise NotImplementedError
