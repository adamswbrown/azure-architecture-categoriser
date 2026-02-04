"""Pydantic schemas for modernization options configuration.

This module defines the data models for technology-to-Azure-service
modernization mappings, loaded from Modernisation_Options.csv.
"""

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class ModernizationStrategy(str, Enum):
    """Migration strategy classification."""

    PAAS = "PaaS"
    IAAS = "IaaS"
    ELIMINATE = "Eliminate"
    SAAS = "SaaS"


class ModernizationComplexity(str, Enum):
    """Complexity level for modernization."""

    EASY = "Easy"
    MEDIUM = "Medium"
    HARD = "Hard"


class ApplicableTreatment(str, Enum):
    """Applicable migration treatment (7R framework)."""

    REPLATFORM_REFACTOR = "Replatform/Refactor"
    REPLACE = "Replace"
    REHOST = "Rehost"
    RETIRE = "Retire"
    RETAIN = "Retain"
    RELOCATE = "Relocate"
    REPURCHASE = "Repurchase"


class ModernizationOption(BaseModel):
    """A single modernization option for a technology.

    Represents one row from Modernisation_Options.csv, mapping a source
    technology to an Azure target service with associated metadata.
    """

    server_sub_category: str = Field(
        description="Category/group of the source technology"
    )
    friendly_name: str = Field(description="Display name of the source technology")
    modernisation_candidate: str = Field(
        description="Target Azure service or action (e.g., 'Azure App Service', 'Eliminate')"
    )
    modernisation_treatment: str = Field(
        description="Full mapping name (e.g., '.NET-to-Azure App Service')"
    )
    default_flag: bool = Field(
        default=False, description="Whether this is the recommended default option"
    )
    modernisation_strategy: str = Field(
        description="Migration strategy: PaaS, IaaS, Eliminate, SaaS"
    )
    modernisation_complexity: str = Field(
        description="Complexity level: Easy, Medium, Hard"
    )
    applicable_treatment: str = Field(
        description="7R treatment: Replatform/Refactor, Replace, etc."
    )
    complexity_score: int = Field(
        default=0, ge=0, le=4, description="Numeric complexity score (0-4)"
    )
    migration_goal_category: Optional[str] = Field(
        default=None, description="Category for migration goals (e.g., 'web_approach')"
    )
    combo_flag: bool = Field(
        default=False, description="Whether this is a combo/combined option"
    )
    light_modernisation_id: Optional[int] = Field(
        default=None, description="ID for light modernization path"
    )
    modernisation_focused_id: Optional[int] = Field(
        default=None, description="ID for focused modernization path"
    )
    key_benefits: Optional[str] = Field(
        default=None, description="Key benefits of this modernization option"
    )
    modernisation_candidate_description: Optional[str] = Field(
        default=None, description="Description of the Azure target service"
    )
    modernisation_candidate_logo: Optional[str] = Field(
        default=None, description="URL to the Azure service logo"
    )

    class Config:
        """Pydantic configuration."""

        str_strip_whitespace = True


class TechnologyGroup(BaseModel):
    """A technology with all its modernization options.

    Groups all ModernizationOption entries that share the same friendly_name.
    """

    friendly_name: str = Field(description="Technology display name")
    server_sub_category: str = Field(description="Technology category/group")
    options: list[ModernizationOption] = Field(
        default_factory=list, description="Available modernization options"
    )

    @property
    def default_option(self) -> Optional[ModernizationOption]:
        """Get the default (recommended) option for this technology."""
        for opt in self.options:
            if opt.default_flag:
                return opt
        return self.options[0] if self.options else None

    @property
    def paas_options(self) -> list[ModernizationOption]:
        """Get all PaaS modernization options."""
        return [o for o in self.options if o.modernisation_strategy == "PaaS"]

    @property
    def iaas_options(self) -> list[ModernizationOption]:
        """Get all IaaS modernization options."""
        return [o for o in self.options if o.modernisation_strategy == "IaaS"]


class ModernizationConfig(BaseModel):
    """Complete modernization configuration.

    Contains all technology-to-Azure mappings loaded from CSV.
    """

    options: list[ModernizationOption] = Field(
        default_factory=list, description="All modernization options"
    )

    @property
    def technology_count(self) -> int:
        """Number of unique technologies."""
        return len(set(o.friendly_name for o in self.options))

    @property
    def option_count(self) -> int:
        """Total number of modernization options."""
        return len(self.options)

    def get_technologies(self) -> list[str]:
        """Get sorted list of unique technology names."""
        return sorted(set(o.friendly_name for o in self.options))

    def get_categories(self) -> list[str]:
        """Get sorted list of unique categories."""
        return sorted(set(o.server_sub_category for o in self.options))

    def get_strategies(self) -> list[str]:
        """Get sorted list of unique strategies."""
        return sorted(set(o.modernisation_strategy for o in self.options))

    def get_options_for_technology(
        self, friendly_name: str
    ) -> list[ModernizationOption]:
        """Get all options for a specific technology."""
        return [o for o in self.options if o.friendly_name == friendly_name]

    def get_technology_groups(self) -> list[TechnologyGroup]:
        """Group options by technology name."""
        groups: dict[str, TechnologyGroup] = {}
        for opt in self.options:
            if opt.friendly_name not in groups:
                groups[opt.friendly_name] = TechnologyGroup(
                    friendly_name=opt.friendly_name,
                    server_sub_category=opt.server_sub_category,
                    options=[],
                )
            groups[opt.friendly_name].options.append(opt)
        return sorted(groups.values(), key=lambda g: g.friendly_name)

    def filter_by_category(self, category: str) -> "ModernizationConfig":
        """Filter options by category."""
        return ModernizationConfig(
            options=[o for o in self.options if o.server_sub_category == category]
        )

    def filter_by_strategy(self, strategy: str) -> "ModernizationConfig":
        """Filter options by strategy."""
        return ModernizationConfig(
            options=[o for o in self.options if o.modernisation_strategy == strategy]
        )

    def search(self, query: str) -> "ModernizationConfig":
        """Search options by technology name or candidate."""
        query_lower = query.lower()
        return ModernizationConfig(
            options=[
                o
                for o in self.options
                if query_lower in o.friendly_name.lower()
                or query_lower in o.modernisation_candidate.lower()
            ]
        )

    def to_compatibility_mappings(self) -> dict[str, dict[str, str]]:
        """Convert to the legacy DEFAULT_COMPATIBILITY_MAPPINGS format.

        This provides backward compatibility with the existing
        DrMigrateContextGenerator implementation.

        Returns:
            Dictionary mapping technology names to their Azure pathways.
        """
        mappings: dict[str, dict[str, str]] = {}

        for group in self.get_technology_groups():
            default_opt = group.default_option
            if not default_opt:
                continue

            # Find options by strategy type
            paas_opts = group.paas_options
            iaas_opts = group.iaas_options

            # Build the mapping
            mapping: dict[str, str] = {
                "azure_equivalent": default_opt.modernisation_candidate,
            }

            # Set rehost (IaaS option or default)
            if iaas_opts:
                mapping["rehost"] = "Azure Virtual Machines"
            else:
                mapping["rehost"] = "Azure Virtual Machines"

            # Set replatform (default PaaS option)
            if default_opt.modernisation_strategy == "PaaS":
                mapping["replatform"] = default_opt.modernisation_candidate
            elif paas_opts:
                mapping["replatform"] = paas_opts[0].modernisation_candidate
            else:
                mapping["replatform"] = "Azure Virtual Machines"

            # Set refactor (most advanced PaaS option)
            container_opts = [
                o
                for o in paas_opts
                if "Container" in o.modernisation_candidate
                or "Kubernetes" in o.modernisation_candidate
            ]
            if container_opts:
                mapping["refactor"] = container_opts[0].modernisation_candidate
            elif paas_opts:
                # Use the hardest complexity PaaS option
                hard_opts = [
                    o for o in paas_opts if o.modernisation_complexity == "Hard"
                ]
                if hard_opts:
                    mapping["refactor"] = hard_opts[0].modernisation_candidate
                else:
                    mapping["refactor"] = mapping["replatform"]
            else:
                mapping["refactor"] = "Assess for containerization"

            # Build modernization path
            path = ["Azure Virtual Machines"]
            if mapping["replatform"] != "Azure Virtual Machines":
                path.append(mapping["replatform"])
            if (
                mapping["refactor"] != mapping["replatform"]
                and mapping["refactor"] != "Assess for containerization"
            ):
                path.append(mapping["refactor"])
            mapping["modernization_path"] = path  # type: ignore

            # Add notes from default option
            if default_opt.key_benefits:
                mapping["notes"] = default_opt.key_benefits

            mappings[group.friendly_name] = mapping

        # Add default fallback
        mappings["_default"] = {
            "rehost": "Azure Virtual Machines",
            "replatform": "Azure Virtual Machines",
            "refactor": "Assess for containerization",
            "azure_equivalent": "Azure Virtual Machines",
            "modernization_path": ["Azure Virtual Machines"],
            "notes": "Unknown technology - recommend assessment for modernization options.",
        }

        return mappings
