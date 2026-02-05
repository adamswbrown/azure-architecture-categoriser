"""LLM-based semantic extractor for architecture documentation.

This module handles extractions requiring semantic understanding that
rule-based patterns cannot reliably capture, such as:
- Intended audience classification
- Maturity tier determination
- Key tradeoff summarization
- Limitation refinement

Supports multiple LLM providers: OpenAI, Anthropic, or mock for testing.
"""

import json
import os
import re
from dataclasses import dataclass, field
from typing import Optional, Protocol

from .content_analyzer import RuleBasedExtractionResult
from .schema import IntendedAudience, MaturityTier


@dataclass
class LLMExtractionResult:
    """Results from LLM-based semantic extraction."""

    intended_audience: Optional[IntendedAudience] = None
    maturity_tier: Optional[MaturityTier] = None
    key_tradeoffs: list[str] = field(default_factory=list)
    explicit_limitations: list[str] = field(default_factory=list)

    # Metadata
    model_used: str = "unknown"
    tokens_used: int = 0
    extraction_successful: bool = False
    error_message: Optional[str] = None


class LLMProvider(Protocol):
    """Protocol for LLM providers."""

    def extract(self, prompt: str) -> tuple[str, int]:
        """Extract information using the LLM.

        Args:
            prompt: The prompt to send to the LLM

        Returns:
            Tuple of (response_text, tokens_used)
        """
        ...


class OpenAIProvider:
    """OpenAI LLM provider."""

    def __init__(self, model: str = "gpt-4o-mini", api_key: Optional[str] = None):
        self.model = model
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        self._client = None

    def _get_client(self):
        if self._client is None:
            try:
                from openai import OpenAI
                self._client = OpenAI(api_key=self.api_key)
            except ImportError:
                raise ImportError("openai package required. Install with: pip install openai")
        return self._client

    def extract(self, prompt: str) -> tuple[str, int]:
        client = self._get_client()
        response = client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,  # Low temperature for consistent extraction
            max_tokens=1000,
        )
        text = response.choices[0].message.content or ""
        tokens = response.usage.total_tokens if response.usage else 0
        return text, tokens


class AnthropicProvider:
    """Anthropic Claude LLM provider."""

    def __init__(self, model: str = "claude-3-haiku-20240307", api_key: Optional[str] = None):
        self.model = model
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        self._client = None

    def _get_client(self):
        if self._client is None:
            try:
                from anthropic import Anthropic
                self._client = Anthropic(api_key=self.api_key)
            except ImportError:
                raise ImportError("anthropic package required. Install with: pip install anthropic")
        return self._client

    def extract(self, prompt: str) -> tuple[str, int]:
        client = self._get_client()
        response = client.messages.create(
            model=self.model,
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}],
        )
        text = response.content[0].text if response.content else ""
        tokens = response.usage.input_tokens + response.usage.output_tokens
        return text, tokens


class MockProvider:
    """Mock LLM provider for testing without API calls."""

    def __init__(self):
        self.model = "mock"

    def extract(self, prompt: str) -> tuple[str, int]:
        """Generate mock extraction based on prompt content analysis.

        Uses the rule-based audience signals in the prompt to make informed decisions.
        """
        prompt_lower = prompt.lower()

        # Parse audience signals from prompt (format: "Audience signals: {...}")
        import re
        signals_match = re.search(r'audience signals:\s*(\{[^}]+\})', prompt_lower)
        signals = {}
        if signals_match:
            try:
                # Parse JSON-formatted signals (uses double quotes)
                signal_text = signals_match.group(1)
                for key in ['poc_positive', 'poc_negative', 'production_positive',
                           'baseline_positive', 'mission_critical_positive']:
                    # Match both single and double quote formats
                    match = re.search(rf'["\']?{key}["\']?:\s*(\d+)', signal_text)
                    if match:
                        signals[key] = int(match.group(1))
            except Exception:
                pass

        # Determine audience based on signals (priority order)
        mission_score = signals.get('mission_critical_positive', 0)
        production_score = signals.get('production_positive', 0)
        poc_positive = signals.get('poc_positive', 0)
        poc_negative = signals.get('poc_negative', 0)
        baseline_score = signals.get('baseline_positive', 0)

        # POC negative signals override everything - "not designed for production"
        if poc_negative >= 3:
            audience = "poc"
            maturity = "basic"
            tradeoffs = ["Cost over reliability", "Simplicity over scalability"]
            limitations = ["Not suitable for production", "Limited availability guarantees"]
        # Mission-critical requires strong signals AND no POC negatives
        # Note: Only check "99.99" in the document content section (first ~4000 chars), not the instructions
        elif mission_score >= 10:
            audience = "mission_critical"
            maturity = "mission_critical"
            tradeoffs = ["Reliability over cost", "Availability over simplicity"]
            limitations = ["Requires significant investment", "High operational complexity"]
        elif poc_positive >= 10 and production_score < 5:
            audience = "poc"
            maturity = "basic"
            tradeoffs = ["Cost over reliability", "Simplicity over scalability"]
            limitations = ["Not suitable for production", "Limited availability guarantees"]
        elif baseline_score >= 5:
            audience = "baseline"
            maturity = "baseline"
            tradeoffs = ["Foundation for production", "Zone-redundancy included"]
            limitations = ["May require customization for specific needs"]
        elif production_score >= 3 and poc_negative < 2:
            audience = "production"
            maturity = "standard"
            tradeoffs = ["Balanced cost and reliability", "Standard scaling patterns"]
            limitations = ["Standard limitations apply"]
        elif mission_score >= 5:
            # Lower threshold for mission-critical if no other matches
            audience = "mission_critical"
            maturity = "mission_critical"
            tradeoffs = ["Reliability over cost", "Availability over simplicity"]
            limitations = ["Requires significant investment", "High operational complexity"]
        else:
            # Fallback based on keywords
            if "mission-critical" in prompt_lower:
                audience = "mission_critical"
                maturity = "mission_critical"
            elif "baseline" in prompt_lower:
                audience = "baseline"
                maturity = "baseline"
            elif "not.*production" in prompt_lower or "isn't.*production" in prompt_lower:
                audience = "poc"
                maturity = "basic"
            else:
                audience = "baseline"
                maturity = "standard"

            tradeoffs = ["Cost vs reliability", "Simplicity vs scalability"]
            limitations = ["Standard limitations apply"]

        response = json.dumps({
            "intended_audience": audience,
            "maturity_tier": maturity,
            "key_tradeoffs": tradeoffs,
            "explicit_limitations": limitations
        })

        return response, 100


EXTRACTION_PROMPT_TEMPLATE = """Analyze this Azure architecture documentation and extract the following metadata.

DOCUMENT CONTENT (first 4000 chars):
---
{content}
---

RULE-BASED SIGNALS DETECTED:
- SLO target: {slo}
- WAF pillars covered: {waf_pillars}
- Design patterns: {design_patterns}
- Team prerequisites: {prerequisites}
- Upgrade paths: {upgrade_paths}
- Audience signals: {audience_signals}
- Raw limitations found: {raw_limitations}

TASK: Based on the document content AND the rule-based signals above, determine:

1. INTENDED_AUDIENCE: Who is this architecture designed for?
   - "poc" = Proof of concept, learning, evaluation, NOT for production
   - "development" = Dev/test environments only
   - "baseline" = Production starting point, foundational
   - "production" = Production-ready, enterprise deployment
   - "mission_critical" = High availability, 99.99%+ SLO, business-critical

   IMPORTANT: If the document says "not designed for production" or "not meant for production",
   the answer is "poc" even if it mentions production guidance for later.

2. MATURITY_TIER: What level of architectural maturity does this represent?
   - "basic" = Learning-focused, minimal features, cost-optimized over reliability
   - "baseline" = Production foundation, zone-redundant, WAF, private networking
   - "standard" = Common production patterns, standard SLAs
   - "advanced" = Enhanced features, multi-region options, advanced security
   - "mission_critical" = Maximum reliability, 99.99%+ SLO, comprehensive DR

3. KEY_TRADEOFFS: What are the 2-4 key design tradeoffs mentioned? (e.g., "Cost over reliability")

4. EXPLICIT_LIMITATIONS: What limitations are explicitly stated? Refine the raw limitations into clean statements.

Respond ONLY with valid JSON in this exact format:
{{
  "intended_audience": "<poc|development|baseline|production|mission_critical>",
  "maturity_tier": "<basic|baseline|standard|advanced|mission_critical>",
  "key_tradeoffs": ["tradeoff 1", "tradeoff 2"],
  "explicit_limitations": ["limitation 1", "limitation 2"]
}}
"""


class LLMExtractor:
    """Extracts semantic metadata using LLM analysis."""

    def __init__(
        self,
        provider: Optional[LLMProvider] = None,
        provider_name: str = "auto"
    ):
        """Initialize the LLM extractor.

        Args:
            provider: LLM provider instance. If None, auto-detects from env vars.
            provider_name: "openai", "anthropic", "mock", or "auto" (default)
        """
        if provider:
            self.provider = provider
        else:
            self.provider = self._auto_detect_provider(provider_name)

    def _auto_detect_provider(self, provider_name: str) -> LLMProvider:
        """Auto-detect and initialize the appropriate LLM provider."""
        if provider_name == "mock":
            return MockProvider()

        if provider_name == "openai" or (
            provider_name == "auto" and os.environ.get("OPENAI_API_KEY")
        ):
            return OpenAIProvider()

        if provider_name == "anthropic" or (
            provider_name == "auto" and os.environ.get("ANTHROPIC_API_KEY")
        ):
            return AnthropicProvider()

        # Default to mock if no API keys found
        return MockProvider()

    def extract(
        self,
        content: str,
        rule_based_result: RuleBasedExtractionResult,
        title: str = ""
    ) -> LLMExtractionResult:
        """Extract semantic metadata using LLM.

        Args:
            content: Full markdown content (will be truncated)
            rule_based_result: Results from rule-based analysis
            title: Document title for context

        Returns:
            LLMExtractionResult with extracted metadata
        """
        result = LLMExtractionResult()

        try:
            # Build prompt with rule-based signals
            prompt = self._build_prompt(content, rule_based_result, title)

            # Call LLM
            response_text, tokens = self.provider.extract(prompt)
            result.tokens_used = tokens
            result.model_used = getattr(self.provider, 'model', 'unknown')

            # Parse response
            parsed = self._parse_response(response_text)

            if parsed:
                result.intended_audience = parsed.get("intended_audience")
                result.maturity_tier = parsed.get("maturity_tier")
                result.key_tradeoffs = parsed.get("key_tradeoffs", [])
                result.explicit_limitations = parsed.get("explicit_limitations", [])
                result.extraction_successful = True
            else:
                result.error_message = "Failed to parse LLM response"

        except Exception as e:
            result.error_message = str(e)
            result.extraction_successful = False

        return result

    def _build_prompt(
        self,
        content: str,
        rule_based: RuleBasedExtractionResult,
        title: str
    ) -> str:
        """Build the extraction prompt with context."""
        # Truncate content to avoid token limits
        truncated_content = content[:4000]
        if title:
            truncated_content = f"TITLE: {title}\n\n{truncated_content}"

        return EXTRACTION_PROMPT_TEMPLATE.format(
            content=truncated_content,
            slo=rule_based.target_slo or "Not detected",
            waf_pillars=", ".join(p.value for p in rule_based.waf_pillars) or "None",
            design_patterns=", ".join(p.value for p in rule_based.design_patterns) or "None",
            prerequisites=", ".join(rule_based.team_prerequisites) or "None",
            upgrade_paths=", ".join(rule_based.upgrade_paths[:3]) or "None",
            audience_signals=json.dumps(rule_based.audience_signals) if rule_based.audience_signals else "{}",
            raw_limitations="; ".join(rule_based.raw_limitations[:5]) or "None detected"
        )

    def _parse_response(self, response: str) -> Optional[dict]:
        """Parse JSON response from LLM."""
        # Try to extract JSON from response
        json_match = re.search(r'\{[^{}]*\}', response, re.DOTALL)
        if not json_match:
            # Try multiline JSON
            json_match = re.search(r'\{[\s\S]*?\}', response)

        if json_match:
            try:
                data = json.loads(json_match.group())

                # Validate and convert enum values
                result = {}

                # Intended audience
                audience = data.get("intended_audience", "").lower()
                try:
                    result["intended_audience"] = IntendedAudience(audience)
                except ValueError:
                    result["intended_audience"] = None

                # Maturity tier
                maturity = data.get("maturity_tier", "").lower()
                try:
                    result["maturity_tier"] = MaturityTier(maturity)
                except ValueError:
                    result["maturity_tier"] = None

                # Lists
                result["key_tradeoffs"] = data.get("key_tradeoffs", [])
                if not isinstance(result["key_tradeoffs"], list):
                    result["key_tradeoffs"] = []

                result["explicit_limitations"] = data.get("explicit_limitations", [])
                if not isinstance(result["explicit_limitations"], list):
                    result["explicit_limitations"] = []

                return result

            except json.JSONDecodeError:
                pass

        return None


def extract_semantic_metadata(
    content: str,
    rule_based_result: RuleBasedExtractionResult,
    title: str = "",
    provider_name: str = "auto"
) -> LLMExtractionResult:
    """Convenience function for LLM extraction.

    Args:
        content: Full markdown content
        rule_based_result: Results from rule-based analysis
        title: Document title
        provider_name: "openai", "anthropic", "mock", or "auto"

    Returns:
        LLMExtractionResult with extracted metadata
    """
    extractor = LLMExtractor(provider_name=provider_name)
    return extractor.extract(content, rule_based_result, title)
