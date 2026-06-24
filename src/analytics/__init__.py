"""Analytics package - class-level aggregation, trends, and risk identification."""

from src.analytics.class_aggregator import ClassAggregator
from src.analytics.difficulty_correlator import DifficultyCorrelator
from src.analytics.risk_identifier import RiskIdentifier
from src.analytics.trend_analyzer import TrendAnalyzer

__all__ = [
    "ClassAggregator",
    "DifficultyCorrelator",
    "RiskIdentifier",
    "TrendAnalyzer",
]
