"""Rule-based content analyzer for extracting metadata from architecture documentation.

This module extracts structured information from markdown content using
regex patterns and heuristics. It handles deterministic extractions like
SLO percentages, WAF pillar sections, technology keywords, and design patterns.

For semantic extractions (audience, tradeoffs), see llm_extractor.py.
"""

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from .schema import (
    DesignPattern,
    WellArchitectedPillar,
)


@dataclass
class RuleBasedExtractionResult:
    """Results from rule-based content analysis."""

    # SLO/SLA
    target_slo: Optional[str] = None

    # Well-Architected Framework pillars with dedicated sections
    waf_pillars: list[WellArchitectedPillar] = field(default_factory=list)

    # Design patterns detected
    design_patterns: list[DesignPattern] = field(default_factory=list)

    # Team prerequisites (skills/technologies)
    team_prerequisites: list[str] = field(default_factory=list)

    # Upgrade paths (links to more robust alternatives)
    upgrade_paths: list[str] = field(default_factory=list)

    # Raw limitation sentences (for LLM refinement)
    raw_limitations: list[str] = field(default_factory=list)

    # Audience hints (raw signals, not final classification)
    audience_signals: dict = field(default_factory=dict)


class ContentAnalyzer:
    """Extracts metadata from architecture documentation using rule-based analysis."""

    # SLO/SLA patterns
    SLO_PATTERNS = [
        r"(\d{2}\.\d+)[\s-]*(?:percent|%)\s*(?:availability|SLA|SLO|uptime)",
        r"(?:SLA|SLO|availability|uptime)\s*(?:of\s*)?(\d{2}\.\d+)",
        r"(\d{2}\.\d+)%\s*(?:service[- ]level|availability)",
        r"target.*?(\d{2}\.\d+)%",
    ]

    # WAF pillar section patterns (markdown headings)
    WAF_PILLAR_PATTERNS = {
        WellArchitectedPillar.RELIABILITY: r"#{2,3}\s*Reliability\b",
        WellArchitectedPillar.SECURITY: r"#{2,3}\s*Security\b",
        WellArchitectedPillar.COST_OPTIMIZATION: r"#{2,3}\s*Cost\s*(?:Optimization)?\b",
        WellArchitectedPillar.OPERATIONAL_EXCELLENCE: r"#{2,3}\s*Operational\s*Excellence\b",
        WellArchitectedPillar.PERFORMANCE_EFFICIENCY: r"#{2,3}\s*Performance\s*(?:Efficiency)?\b",
    }

    # Design pattern detection
    DESIGN_PATTERN_PATTERNS = {
        DesignPattern.ACTIVE_ACTIVE: r"active[- ]active",
        DesignPattern.ACTIVE_PASSIVE: r"active[- ]passive",
        DesignPattern.BLUE_GREEN: r"blue[- ]green",
        DesignPattern.CANARY: r"canary\s+(?:deployment|release)",
        DesignPattern.ZERO_TRUST: r"zero[- ]trust",
        DesignPattern.PRIVATE_NETWORKING: r"private[- ](?:endpoint|link|network)",
        DesignPattern.HUB_SPOKE: r"hub[- ](?:and[- ])?spoke",
        DesignPattern.MICROSERVICES: r"microservices?\s+(?:architecture|pattern)",
        DesignPattern.EVENT_DRIVEN: r"event[- ]driven\s+(?:architecture|pattern)",
        DesignPattern.CQRS: r"\bCQRS\b|command[- ]query",
        DesignPattern.SAGA: r"\bsaga\s+pattern",
        DesignPattern.CIRCUIT_BREAKER: r"circuit[- ]breaker",
    }

    # Technology/skill prerequisites
    SKILL_PATTERNS = {
        "kubernetes": r"\b(?:kubernetes|k8s|AKS)\b",
        "containers": r"\b(?:container|docker|helm|dockerfile)\b",
        "devops": r"\b(?:devops|ci/cd|pipeline|github\s+actions|azure\s+devops)\b",
        "terraform": r"\b(?:terraform|infrastructure\s+as\s+code|IaC|bicep|arm\s+template)\b",
        "gitops": r"\b(?:gitops|flux|argocd|argo\s+cd)\b",
        "serverless": r"\b(?:serverless|azure\s+functions|logic\s+apps)\b",
        "networking": r"\b(?:vnet|virtual\s+network|expressroute|vpn\s+gateway|front\s+door)\b",
        "security": r"\b(?:zero\s+trust|waf|application\s+gateway|firewall|defender)\b",
        "monitoring": r"\b(?:azure\s+monitor|application\s+insights|log\s+analytics|prometheus|grafana)\b",
        "databases": r"\b(?:cosmos\s+db|sql\s+database|postgresql|mysql|redis)\b",
    }

    # Audience signal patterns (raw signals, will be refined by LLM)
    AUDIENCE_SIGNAL_PATTERNS = {
        "poc_positive": [
            r"proof[- ]of[- ]concept",
            r"\bPOC\b",
            r"learning\s+purposes",
            r"evaluation\s+(?:purposes|only)",
            r"introductory\s+setup",
            r"getting\s+started",
        ],
        "poc_negative": [
            r"isn't\s+(?:meant|designed|intended)\s+for\s+production",
            r"not\s+(?:meant|designed|intended)\s+for\s+production",
            r"not\s+production[- ]ready",
        ],
        "production_positive": [
            r"production[- ]ready",
            r"production\s+environments",
            r"enterprise[- ]grade",
            r"designed\s+for\s+production",
        ],
        "baseline_positive": [
            r"baseline\s+architecture",
            r"starting\s+point",
            r"foundational",
            r"reference\s+implementation",
        ],
        "mission_critical_positive": [
            r"mission[- ]critical",
            r"business[- ]critical",
            r"99\.99",
            r"high\s+availability",
            r"disaster\s+recovery",
        ],
    }

    # Limitation sentence patterns
    LIMITATION_PATTERNS = [
        r"(?:not|doesn't|isn't|aren't|don't)\s+(?:designed|intended|suitable|recommended)\s+for[^.]+\.",
        r"(?:lacks?|omits?|excludes?|without)\s+[^.]+\.",
        r"(?:this\s+architecture\s+)?(?:doesn't|does\s+not)\s+(?:include|support|provide)[^.]+\.",
        r"(?:not\s+)?suitable\s+for[^.]+\.",
    ]

    # Upgrade path patterns (links to more robust alternatives)
    UPGRADE_PATH_KEYWORDS = [
        "baseline",
        "zone-redundant",
        "multi-region",
        "mission-critical",
        "highly-available",
        "production",
        "enterprise",
    ]

    def __init__(self):
        """Initialize the content analyzer."""
        pass

    def analyze(self, content: str, file_path: Optional[Path] = None) -> RuleBasedExtractionResult:
        """Analyze document content and extract rule-based metadata.

        Args:
            content: Full markdown content of the architecture document
            file_path: Optional path for context (e.g., detecting maturity from path)

        Returns:
            RuleBasedExtractionResult with extracted metadata
        """
        result = RuleBasedExtractionResult()

        # Extract SLO
        result.target_slo = self._extract_slo(content)

        # Extract WAF pillars
        result.waf_pillars = self._extract_waf_pillars(content)

        # Extract design patterns
        result.design_patterns = self._extract_design_patterns(content)

        # Extract team prerequisites
        result.team_prerequisites = self._extract_prerequisites(content)

        # Extract upgrade paths
        result.upgrade_paths = self._extract_upgrade_paths(content)

        # Extract raw limitations (for LLM refinement)
        result.raw_limitations = self._extract_raw_limitations(content)

        # Extract audience signals (for LLM classification)
        result.audience_signals = self._extract_audience_signals(content)

        return result

    def _extract_slo(self, content: str) -> Optional[str]:
        """Extract SLO/SLA percentage from content."""
        slo_values = set()

        for pattern in self.SLO_PATTERNS:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                # Validate it's a reasonable SLO (90-100%)
                try:
                    value = float(match)
                    if 90.0 <= value <= 100.0:
                        slo_values.add(match)
                except ValueError:
                    continue

        # Return the highest SLO found (most specific target)
        if slo_values:
            return max(slo_values, key=float)
        return None

    def _extract_waf_pillars(self, content: str) -> list[WellArchitectedPillar]:
        """Extract Well-Architected Framework pillars with dedicated sections."""
        pillars = []

        for pillar, pattern in self.WAF_PILLAR_PATTERNS.items():
            if re.search(pattern, content, re.IGNORECASE):
                pillars.append(pillar)

        return pillars

    def _extract_design_patterns(self, content: str) -> list[DesignPattern]:
        """Extract architectural design patterns mentioned in content."""
        patterns = []

        for pattern_type, regex in self.DESIGN_PATTERN_PATTERNS.items():
            if re.search(regex, content, re.IGNORECASE):
                patterns.append(pattern_type)

        return patterns

    def _extract_prerequisites(self, content: str) -> list[str]:
        """Extract team skill/technology prerequisites."""
        prerequisites = []

        for skill, pattern in self.SKILL_PATTERNS.items():
            if re.search(pattern, content, re.IGNORECASE):
                prerequisites.append(skill)

        return prerequisites

    def _extract_upgrade_paths(self, content: str) -> list[str]:
        """Extract links to more robust architecture alternatives."""
        upgrade_paths = []

        # Find markdown links that suggest upgrade paths
        link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
        matches = re.findall(link_pattern, content)

        for link_text, link_url in matches:
            link_lower = (link_text + link_url).lower()
            for keyword in self.UPGRADE_PATH_KEYWORDS:
                if keyword in link_lower:
                    # Clean up the path
                    clean_path = link_url.strip()
                    if clean_path.startswith('./'):
                        clean_path = clean_path[2:]
                    if clean_path.startswith('../'):
                        clean_path = clean_path[3:]
                    # Remove .yml/.md extensions
                    clean_path = re.sub(r'\.(yml|yaml|md)$', '', clean_path)

                    if clean_path and clean_path not in upgrade_paths:
                        upgrade_paths.append(clean_path)
                    break

        return upgrade_paths[:5]  # Limit to top 5

    def _extract_raw_limitations(self, content: str) -> list[str]:
        """Extract raw limitation sentences for LLM refinement."""
        limitations = []

        for pattern in self.LIMITATION_PATTERNS:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                # Clean up and dedupe
                clean = match.strip()
                if clean and len(clean) > 20 and clean not in limitations:
                    # Filter out false positives (generic statements)
                    if not self._is_false_positive_limitation(clean):
                        limitations.append(clean)

        return limitations[:10]  # Limit to top 10

    def _is_false_positive_limitation(self, text: str) -> bool:
        """Check if a limitation sentence is a false positive."""
        false_positive_indicators = [
            "don't have to",  # "you don't have to manage" is not a limitation
            "doesn't require",  # positive statement
            "without user involvement",  # describing automation
            "don't need to",
            "without requiring",
        ]

        text_lower = text.lower()
        return any(indicator in text_lower for indicator in false_positive_indicators)

    def _extract_audience_signals(self, content: str) -> dict:
        """Extract raw audience signals for LLM classification."""
        signals = {}

        for signal_type, patterns in self.AUDIENCE_SIGNAL_PATTERNS.items():
            matches = []
            for pattern in patterns:
                found = re.findall(pattern, content, re.IGNORECASE)
                matches.extend(found)
            if matches:
                signals[signal_type] = len(matches)

        return signals


def analyze_content(content: str, file_path: Optional[Path] = None) -> RuleBasedExtractionResult:
    """Convenience function to analyze content.

    Args:
        content: Full markdown content
        file_path: Optional file path for context

    Returns:
        RuleBasedExtractionResult with extracted metadata
    """
    analyzer = ContentAnalyzer()
    return analyzer.analyze(content, file_path)
