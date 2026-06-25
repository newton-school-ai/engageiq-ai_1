"""Track engagement change after nudges to measure effectiveness."""

# TODO: Implement full effectiveness tracking


class EffectivenessTracker:
    """Tracks engagement change before and after nudges to measure their effectiveness."""

    def __init__(self, observation_window: float = 60.0):
        self.observation_window = observation_window
        self._pending: list[dict] = []

    def record_nudge(self, timestamp: float, pre_nudge_score: float) -> None:
        """Record that a nudge was sent at the given timestamp."""
        self._pending.append({"timestamp": timestamp, "pre_score": pre_nudge_score})

    def update_score(self, timestamp: float, score: float) -> dict | None:
        """Update with a new engagement score and compute effectiveness if window has elapsed.

        Returns:
            Dict with effectiveness stats, or None if no observation is complete.
        """
        # TODO: Implement effectiveness calculation
        raise NotImplementedError
