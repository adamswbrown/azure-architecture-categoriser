"""Architecture Scoring and Recommendation Engine.

This engine evaluates application contexts against the Azure Architecture Catalog
and returns ranked architecture recommendations with clear reasoning.

Runtime component - does NOT modify the catalog.
"""

from .engine import ScoringEngine
from .schema import (
    ApplicationContext,
    ScoringResult,
    ArchitectureRecommendation,
    ExcludedArchitecture,
    RecommendationSummary,
)

__all__ = [
    "ScoringEngine",
    "ApplicationContext",
    "ScoringResult",
    "ArchitectureRecommendation",
    "ExcludedArchitecture",
    "RecommendationSummary",
]
