"""Scoring Engine - Main Orchestrator.

Orchestrates all phases of the Architecture Scoring and Recommendation Engine.
This is the primary entry point for scoring applications against the catalog.
"""

import json
from pathlib import Path
from typing import Any, Optional

from catalog_builder.schema import ArchitectureCatalog, ArchitectureEntry

from .eligibility_filter import EligibilityFilter
from .explainer import build_scoring_result
from .intent_deriver import IntentDeriver
from .normalizer import ContextNormalizer, load_context_file
from .question_generator import QuestionGenerator
from .schema import (
    ApplicationContext,
    ClarificationQuestion,
    RawContextFile,
    ScoringResult,
)
from .scorer import ArchitectureScorer, ScoringWeights


class ScoringEngine:
    """Main orchestrator for architecture scoring.

    This engine evaluates application contexts against the Azure Architecture
    Catalog and returns ranked recommendations with clear reasoning.

    Usage:
        engine = ScoringEngine()
        engine.load_catalog("architecture-catalog.json")
        result = engine.score("app-context.json")
    """

    MIN_CATALOG_VERSION = "1.0"

    def __init__(self, scoring_weights: Optional[ScoringWeights] = None):
        """Initialize the scoring engine.

        Args:
            scoring_weights: Optional custom scoring weights
        """
        self.catalog: Optional[ArchitectureCatalog] = None
        self.normalizer = ContextNormalizer()
        self.intent_deriver = IntentDeriver()
        self.question_generator = QuestionGenerator()
        self.eligibility_filter = EligibilityFilter()
        self.scorer = ArchitectureScorer(weights=scoring_weights)
        self._warnings: list[str] = []

    def load_catalog(self, catalog_path: str) -> None:
        """Load and validate the architecture catalog.

        Args:
            catalog_path: Path to architecture-catalog.json

        Raises:
            ValueError: If catalog is invalid or version is unsupported
            FileNotFoundError: If catalog file doesn't exist
        """
        path = Path(catalog_path)
        if not path.exists():
            raise FileNotFoundError(f"Catalog not found: {catalog_path}")

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Validate version
        version = data.get("version", "0.0.0")
        if not self._version_compatible(version):
            raise ValueError(
                f"Catalog version {version} is not compatible. "
                f"Minimum required: {self.MIN_CATALOG_VERSION}"
            )

        self.catalog = ArchitectureCatalog.model_validate(data)

    def _version_compatible(self, version: str) -> bool:
        """Check if catalog version is compatible."""
        try:
            major, minor, *_ = version.split(".")
            min_major, min_minor, *_ = self.MIN_CATALOG_VERSION.split(".")
            return (int(major), int(minor)) >= (int(min_major), int(min_minor))
        except (ValueError, AttributeError):
            return False

    def score(
        self,
        context_path: str,
        user_answers: Optional[dict[str, str]] = None,
        max_recommendations: int = 10,
    ) -> ScoringResult:
        """Score an application context against the catalog.

        Args:
            context_path: Path to application context JSON file
            user_answers: Optional answers to clarification questions
            max_recommendations: Maximum recommendations to return

        Returns:
            Complete ScoringResult with recommendations and explanations

        Raises:
            ValueError: If catalog not loaded or context invalid
        """
        if not self.catalog:
            raise ValueError("Catalog not loaded. Call load_catalog() first.")

        self._warnings = []

        # Phase 0: Load and validate context
        context = self._load_context(context_path)

        # Apply user answers if provided
        if user_answers:
            context.user_answers = user_answers

        # Execute scoring pipeline
        return self._execute_pipeline(context, user_answers, max_recommendations)

    def score_context(
        self,
        context: ApplicationContext,
        user_answers: Optional[dict[str, str]] = None,
        max_recommendations: int = 10,
    ) -> ScoringResult:
        """Score a pre-loaded application context.

        Args:
            context: Normalized ApplicationContext
            user_answers: Optional answers to clarification questions
            max_recommendations: Maximum recommendations to return

        Returns:
            Complete ScoringResult
        """
        if not self.catalog:
            raise ValueError("Catalog not loaded. Call load_catalog() first.")

        self._warnings = []

        if user_answers:
            context.user_answers = user_answers

        return self._execute_pipeline(context, user_answers, max_recommendations)

    def _load_context(self, context_path: str) -> ApplicationContext:
        """Load and normalize the application context."""
        try:
            return load_context_file(context_path)
        except Exception as e:
            raise ValueError(f"Failed to load context file: {e}")

    def _execute_pipeline(
        self,
        context: ApplicationContext,
        user_answers: Optional[dict[str, str]],
        max_recommendations: int,
    ) -> ScoringResult:
        """Execute the full scoring pipeline.

        Phases:
        1. Normalize (already done in load)
        2. Derive intent
        3. Generate questions (if needed)
        4. Filter eligibility
        5. Score eligible architectures
        6. Generate explanations
        """
        # Phase 2: Derive architectural intent
        intent = self.intent_deriver.derive(context)

        # Phase 3: Apply user answers and generate remaining questions
        if user_answers:
            intent = self.question_generator.apply_answers(context, intent, user_answers)

        questions = self.question_generator.generate_questions(context, intent)

        # Phase 4: Filter eligible architectures
        eligible, excluded = self.eligibility_filter.filter(
            self.catalog.architectures,
            context,
            intent,
        )

        if not eligible:
            self._warnings.append("No eligible architectures found after filtering")

        # Phase 5: Score eligible architectures
        recommendations = self.scorer.score(eligible, context, intent)

        # Limit to max recommendations
        recommendations = recommendations[:max_recommendations]

        # Phase 6: Build final result with explanations
        result = build_scoring_result(
            application_name=context.app_overview.application_name,
            catalog_version=self.catalog.version,
            catalog_count=len(self.catalog.architectures),
            intent=intent,
            questions=questions,
            recommendations=recommendations,
            excluded=excluded,
            warnings=self._warnings,
        )

        return result

    def get_questions(
        self,
        context_path: str,
    ) -> list[ClarificationQuestion]:
        """Get clarification questions for a context without full scoring.

        Useful for interactive UIs that want to collect answers first.

        Args:
            context_path: Path to application context JSON file

        Returns:
            List of clarification questions
        """
        context = self._load_context(context_path)
        intent = self.intent_deriver.derive(context)
        return self.question_generator.generate_questions(context, intent)


def score_application(
    catalog_path: str,
    context_path: str,
    user_answers: Optional[dict[str, str]] = None,
    max_recommendations: int = 10,
) -> ScoringResult:
    """Convenience function to score an application in one call.

    Args:
        catalog_path: Path to architecture-catalog.json
        context_path: Path to application context JSON file
        user_answers: Optional answers to clarification questions
        max_recommendations: Maximum recommendations to return

    Returns:
        Complete ScoringResult
    """
    engine = ScoringEngine()
    engine.load_catalog(catalog_path)
    return engine.score(context_path, user_answers, max_recommendations)


def validate_catalog(catalog_path: str) -> tuple[bool, list[str]]:
    """Validate a catalog file without loading it fully.

    Args:
        catalog_path: Path to catalog file

    Returns:
        Tuple of (is_valid, list of issues)
    """
    issues = []

    path = Path(catalog_path)
    if not path.exists():
        return False, ["Catalog file not found"]

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        return False, [f"Invalid JSON: {e}"]

    # Check required fields
    if "version" not in data:
        issues.append("Missing 'version' field")
    if "architectures" not in data:
        issues.append("Missing 'architectures' field")
    elif not isinstance(data["architectures"], list):
        issues.append("'architectures' must be a list")
    elif len(data["architectures"]) == 0:
        issues.append("Catalog contains no architectures")

    # Check version
    version = data.get("version", "0.0.0")
    try:
        major, minor, *_ = version.split(".")
        if int(major) < 1:
            issues.append(f"Catalog version {version} is below minimum 1.0")
    except ValueError:
        issues.append(f"Invalid version format: {version}")

    return len(issues) == 0, issues


def validate_context(context_path: str) -> tuple[bool, list[str]]:
    """Validate a context file without full processing.

    Args:
        context_path: Path to context file

    Returns:
        Tuple of (is_valid, list of issues)
    """
    issues = []

    path = Path(context_path)
    if not path.exists():
        return False, ["Context file not found"]

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        return False, [f"Invalid JSON: {e}"]

    # Handle array wrapper
    if isinstance(data, list):
        if len(data) != 1:
            issues.append(f"Expected exactly 1 context object, got {len(data)}")
            return False, issues
        data = data[0]

    # Check required fields
    if "app_overview" not in data:
        issues.append("Missing 'app_overview' field")
    elif not isinstance(data["app_overview"], list) or len(data["app_overview"]) == 0:
        issues.append("'app_overview' must be a non-empty list")
    else:
        overview = data["app_overview"][0]
        if "application" not in overview:
            issues.append("Missing 'application' in app_overview")

    return len(issues) == 0, issues
