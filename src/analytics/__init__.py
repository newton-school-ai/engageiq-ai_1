"""Analytics package - class-level aggregation, trends, and risk identification."""

from src.analytics.class_aggregator import ClassAggregator  # noqa: F401
from src.analytics.difficulty_correlator import DifficultyCorrelator  # noqa: F401
from src.analytics.risk_identifier import RiskIdentifier  # noqa: F401
from src.analytics.trend_analyzer import TrendAnalyzer  # noqa: F401

__all__ = [
    "ClassAggregator",
    "DifficultyCorrelator",
    "RiskIdentifier",
    "TrendAnalyzer",
]
