"""Nudge decision logic: when to nudge based on state, duration, history."""
# TODO: Implement full nudge decision logic


class NudgeDecision:
    """Determines whether a nudge should be sent based on engagement state and history."""

    def __init__(self, cooldown_seconds: int = 300, max_nudges_per_session: int = 5):
        self.cooldown_seconds = cooldown_seconds
        self.max_nudges_per_session = max_nudges_per_session
        self._nudge_history: list[float] = []

    def should_nudge(self, engagement_score: float, timestamp: float) -> bool:
        """Decide whether to nudge the student.

        Args:
            engagement_score: Current engagement score (0-100).
            timestamp: Current time in seconds.

        Returns:
            True if a nudge should be sent.
        """
        # TODO: Implement full decision logic
        raise NotImplementedError
