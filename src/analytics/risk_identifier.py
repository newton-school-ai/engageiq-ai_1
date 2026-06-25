"""Identify at-risk students with consistently low engagement."""

# TODO: Implement full risk identification logic


class RiskIdentifier:
    """Identifies at-risk students based on sustained low engagement patterns."""

    def __init__(self, risk_threshold: float = 40.0, min_sessions: int = 3):
        self.risk_threshold = risk_threshold
        self.min_sessions = min_sessions

    def identify(self, student_session_scores: dict[str, list[float]]) -> list[str]:
        """Return list of student IDs considered at-risk.

        Args:
            student_session_scores: Mapping of student_id -> list of per-session scores.

        Returns:
            List of at-risk student IDs.
        """
        # TODO: Implement
        raise NotImplementedError
