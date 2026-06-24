"""Aggregate student engagement into class-level metrics."""
# TODO: Implement full aggregation logic


class ClassAggregator:
    """Aggregates per-student engagement scores into class-level metrics."""

    def aggregate(self, student_scores: dict[str, float]) -> dict:
        """Compute class-level engagement statistics.

        Args:
            student_scores: Mapping of student_id -> engagement score (0-100).

        Returns:
            Dict with keys: mean, median, std, min, max, at_risk_count.
        """
        # TODO: Implement
        raise NotImplementedError
