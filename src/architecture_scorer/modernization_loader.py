"""Utilities for loading and saving modernization options from CSV.

This module provides functions to load the Modernisation_Options.csv file
into Pydantic models and save modifications back to CSV.
"""

import csv
from pathlib import Path
from typing import Optional

from .modernization_schema import ModernizationConfig, ModernizationOption

# CSV file locations (relative to project root)
# The filtered version contains only architecturally-relevant technologies
# (~1210 rows vs 2029 in the full version)
FILTERED_CSV_FILENAME = "Modernisation_Options_Filtered.csv"
FULL_CSV_FILENAME = "Modernisation_Options.csv"

# Default to filtered CSV for better performance and relevance
DEFAULT_CSV_FILENAME = FILTERED_CSV_FILENAME


def find_csv_path(use_full: bool = False) -> Optional[Path]:
    """Find the Modernisation_Options CSV file.

    Searches in order:
    1. MODERNIZATION_OPTIONS_CSV environment variable (takes precedence)
    2. Current working directory
    3. Project root (parent of src/)

    Args:
        use_full: If True, use the full unfiltered CSV. If False (default),
                  use the filtered CSV with architecturally-relevant entries only.

    Returns:
        Path to the CSV file, or None if not found.
    """
    import os

    # Check environment variable first (takes precedence)
    env_path = os.environ.get("MODERNIZATION_OPTIONS_CSV")
    if env_path:
        path = Path(env_path)
        if path.exists():
            return path

    # Determine which filename to use
    csv_filename = FULL_CSV_FILENAME if use_full else FILTERED_CSV_FILENAME

    # Check current directory
    cwd_path = Path.cwd() / csv_filename
    if cwd_path.exists():
        return cwd_path

    # Check project root (this file is in src/architecture_scorer/)
    this_file = Path(__file__)
    project_root = this_file.parent.parent.parent
    root_path = project_root / csv_filename
    if root_path.exists():
        return root_path

    # Fall back to default filename if filtered not found
    if not use_full:
        return find_csv_path(use_full=True)

    return None


def load_modernization_config(
    csv_path: Optional[Path] = None, use_full: bool = False
) -> ModernizationConfig:
    """Load modernization options from CSV file.

    Args:
        csv_path: Path to CSV file. If None, searches default locations.
        use_full: If True and csv_path is None, use the full unfiltered CSV.
                  If False (default), use the filtered CSV with
                  architecturally-relevant entries only (~1210 vs 2029 rows).

    Returns:
        ModernizationConfig containing all options.

    Raises:
        FileNotFoundError: If CSV file not found.
        ValueError: If CSV format is invalid.
    """
    if csv_path is None:
        csv_path = find_csv_path(use_full=use_full)
        if csv_path is None:
            raise FileNotFoundError(
                f"Could not find {FILTERED_CSV_FILENAME} or {FULL_CSV_FILENAME}. "
                "Set MODERNIZATION_OPTIONS_CSV environment variable or "
                "place the file in the project root."
            )

    options: list[ModernizationOption] = []

    with open(csv_path, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)

        for row_num, row in enumerate(reader, start=2):
            try:
                option = _parse_row(row)
                options.append(option)
            except Exception as e:
                raise ValueError(
                    f"Error parsing row {row_num} in {csv_path}: {e}"
                ) from e

    return ModernizationConfig(options=options)


def _parse_row(row: dict[str, str]) -> ModernizationOption:
    """Parse a CSV row into a ModernizationOption.

    Args:
        row: Dictionary from csv.DictReader.

    Returns:
        ModernizationOption instance.
    """
    # Handle numeric fields with defaults
    def parse_int(value: str, default: int = 0) -> int:
        if not value or value.strip() == "":
            return default
        try:
            return int(float(value))
        except (ValueError, TypeError):
            return default

    def parse_bool(value: str) -> bool:
        if not value:
            return False
        return str(value).strip() in ("1", "true", "True", "yes", "Yes")

    def parse_optional_int(value: str) -> Optional[int]:
        if not value or value.strip() == "":
            return None
        try:
            return int(float(value))
        except (ValueError, TypeError):
            return None

    def clean_string(value: Optional[str]) -> str:
        return (value or "").strip()

    def clean_optional_string(value: Optional[str]) -> Optional[str]:
        cleaned = (value or "").strip()
        return cleaned if cleaned else None

    return ModernizationOption(
        server_sub_category=clean_string(row.get("ServerSubCategory")),
        friendly_name=clean_string(row.get("FriendlyName")),
        modernisation_candidate=clean_string(row.get("modernisation_candidate")),
        modernisation_treatment=clean_string(row.get("modernisation_treatment")),
        default_flag=parse_bool(row.get("default_flag", "")),
        modernisation_strategy=clean_string(row.get("modernisation_strategy")),
        modernisation_complexity=clean_string(row.get("modernisation_complexity")),
        applicable_treatment=clean_string(row.get("applicable_treatment")),
        complexity_score=parse_int(row.get("complexity_score", ""), 0),
        migration_goal_category=clean_optional_string(row.get("migration_goal_category")),
        combo_flag=parse_bool(row.get("combo_flag", "")),
        light_modernisation_id=parse_optional_int(row.get("light_modernisation_id", "")),
        modernisation_focused_id=parse_optional_int(row.get("modernisation_focused_id", "")),
        key_benefits=clean_optional_string(row.get("key_benefits")),
        modernisation_candidate_description=clean_optional_string(
            row.get("modernisation_candidate_description")
        ),
        modernisation_candidate_logo=clean_optional_string(
            row.get("modernisation_candidate_logo")
        ),
    )


def save_modernization_config(
    config: ModernizationConfig, csv_path: Path, backup: bool = True
) -> None:
    """Save modernization options to CSV file.

    Args:
        config: ModernizationConfig to save.
        csv_path: Path to output CSV file.
        backup: If True, create a backup of existing file.
    """
    # Create backup if file exists
    if backup and csv_path.exists():
        backup_path = csv_path.with_suffix(".csv.bak")
        import shutil

        shutil.copy2(csv_path, backup_path)

    fieldnames = [
        "ServerSubCategory",
        "FriendlyName",
        "modernisation_candidate",
        "modernisation_treatment",
        "default_flag",
        "modernisation_strategy",
        "modernisation_complexity",
        "applicable_treatment",
        "complexity_score",
        "migration_goal_category",
        "combo_flag",
        "light_modernisation_id",
        "modernisation_focused_id",
        "key_benefits",
        "modernisation_candidate_description",
        "modernisation_candidate_logo",
    ]

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for option in config.options:
            writer.writerow(_option_to_row(option))


def _option_to_row(option: ModernizationOption) -> dict[str, str]:
    """Convert a ModernizationOption to a CSV row dictionary.

    Args:
        option: ModernizationOption to convert.

    Returns:
        Dictionary suitable for csv.DictWriter.
    """
    return {
        "ServerSubCategory": option.server_sub_category,
        "FriendlyName": option.friendly_name,
        "modernisation_candidate": option.modernisation_candidate,
        "modernisation_treatment": option.modernisation_treatment,
        "default_flag": "1" if option.default_flag else "0",
        "modernisation_strategy": option.modernisation_strategy,
        "modernisation_complexity": option.modernisation_complexity,
        "applicable_treatment": option.applicable_treatment,
        "complexity_score": str(option.complexity_score),
        "migration_goal_category": option.migration_goal_category or "",
        "combo_flag": "1" if option.combo_flag else "0",
        "light_modernisation_id": (
            str(option.light_modernisation_id)
            if option.light_modernisation_id is not None
            else ""
        ),
        "modernisation_focused_id": (
            str(option.modernisation_focused_id)
            if option.modernisation_focused_id is not None
            else ""
        ),
        "key_benefits": option.key_benefits or "",
        "modernisation_candidate_description": (
            option.modernisation_candidate_description or ""
        ),
        "modernisation_candidate_logo": option.modernisation_candidate_logo or "",
    }


def add_option(
    config: ModernizationConfig, option: ModernizationOption
) -> ModernizationConfig:
    """Add a new option to the configuration.

    Args:
        config: Existing configuration.
        option: New option to add.

    Returns:
        New ModernizationConfig with the option added.
    """
    return ModernizationConfig(options=[*config.options, option])


def remove_option(
    config: ModernizationConfig, friendly_name: str, modernisation_candidate: str
) -> ModernizationConfig:
    """Remove an option from the configuration.

    Args:
        config: Existing configuration.
        friendly_name: Technology name.
        modernisation_candidate: Azure target to remove.

    Returns:
        New ModernizationConfig with the option removed.
    """
    return ModernizationConfig(
        options=[
            o
            for o in config.options
            if not (
                o.friendly_name == friendly_name
                and o.modernisation_candidate == modernisation_candidate
            )
        ]
    )


def update_option(
    config: ModernizationConfig,
    friendly_name: str,
    modernisation_candidate: str,
    updates: dict,
) -> ModernizationConfig:
    """Update an existing option in the configuration.

    Args:
        config: Existing configuration.
        friendly_name: Technology name.
        modernisation_candidate: Azure target to update.
        updates: Dictionary of field updates.

    Returns:
        New ModernizationConfig with the option updated.
    """
    new_options = []
    for o in config.options:
        if (
            o.friendly_name == friendly_name
            and o.modernisation_candidate == modernisation_candidate
        ):
            # Create updated option
            data = o.model_dump()
            data.update(updates)
            new_options.append(ModernizationOption(**data))
        else:
            new_options.append(o)

    return ModernizationConfig(options=new_options)


def set_default_option(
    config: ModernizationConfig, friendly_name: str, modernisation_candidate: str
) -> ModernizationConfig:
    """Set the default option for a technology.

    Clears default_flag on all other options for the technology and
    sets it on the specified option.

    Args:
        config: Existing configuration.
        friendly_name: Technology name.
        modernisation_candidate: Azure target to set as default.

    Returns:
        New ModernizationConfig with updated default flags.
    """
    new_options = []
    for o in config.options:
        if o.friendly_name == friendly_name:
            # Update default flag based on whether this is the target
            is_default = o.modernisation_candidate == modernisation_candidate
            if o.default_flag != is_default:
                data = o.model_dump()
                data["default_flag"] = is_default
                new_options.append(ModernizationOption(**data))
            else:
                new_options.append(o)
        else:
            new_options.append(o)

    return ModernizationConfig(options=new_options)


def get_compatibility_mappings(
    csv_path: Optional[Path] = None, use_full: bool = False
) -> dict[str, dict[str, str]]:
    """Load CSV and convert to legacy compatibility mappings format.

    This is a convenience function for use by DrMigrateContextGenerator.

    Args:
        csv_path: Path to CSV file. If None, searches default locations.
        use_full: If True and csv_path is None, use the full unfiltered CSV.
                  If False (default), use the filtered CSV.

    Returns:
        Dictionary in DEFAULT_COMPATIBILITY_MAPPINGS format.
    """
    config = load_modernization_config(csv_path, use_full=use_full)
    return config.to_compatibility_mappings()
