"""Map engagement dips to lecture segments to identify difficult topics."""
# TODO: Implement full correlator logic


class DifficultyCorrelator:
    """Maps engagement dips to lecture timestamps to flag difficult segments."""

    def correlate(
        self, engagement_timeline: list[tuple[float, float]], threshold: float = 40.0
    ) -> list[dict]:
        """Find lecture segments where engagement dropped below threshold.

        Args:
            engagement_timeline: List of (timestamp_seconds, score) tuples.
            threshold: Engagement score below which a segment is flagged.

        Returns:
            List of dicts with keys: start, end, mean_score.
        """
        # TODO: Implement
        raise NotImplementedError
