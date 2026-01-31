"""
Frontmatter handler for parsing and updating YAML frontmatter in daily and weekly notes.
"""

# ----- Built-In Modules-----
import datetime
from pathlib import Path
from typing import Optional

# ----- Third-Party Modules-----
import yaml

# ----- Core Modules-----
from src.core.config import DAILY_JOURNAL_PATH, WEEKLY_JOURNAL_PATH

# Field schemas for daily and weekly notes
DAILY_FIELDS = {
    "book": {"type": "float", "range": (0, 24), "section": "Tracking"},
    "learn_blender": {"type": "float", "range": (0, 24), "section": "Tracking"},
    "learn_python": {"type": "float", "range": (0, 24), "section": "Tracking"},
    "learn_ahk": {"type": "float", "range": (0, 24), "section": "Tracking"},
    "morning_mood": {"type": "int", "range": (0, 10), "section": "Mood"},
    "evening_mood": {"type": "int", "range": (0, 10), "section": "Mood"},
    "MAD": {"type": "int", "range": (0, 4), "section": "Metrics"},
    "PAD": {"type": "int", "range": (0, 10), "section": "Metrics"},
    "fajr_sunnah": {"type": "bool", "section": "Spiritual"},
    "prayers": {"type": "int", "range": (0, 5), "section": "Spiritual"},
}

WEEKLY_FIELDS = {
    "weekly_overview": {"type": "float", "range": (0, 168), "section": "Overview"},
    "overall_mood": {"type": "float", "range": (0, 10), "section": "Mood"},
    "reading": {"type": "float", "range": (0, 168), "section": "Tracking"},
    "learn_blender": {"type": "float", "range": (0, 168), "section": "Tracking"},
    "learn_python": {"type": "float", "range": (0, 168), "section": "Tracking"},
    "learn_ahk": {"type": "float", "range": (0, 168), "section": "Tracking"},
    "MAD": {"type": "int", "range": (0, 28), "section": "Metrics"},
    "PAD": {"type": "int", "range": (0, 70), "section": "Metrics"},
    "fajr_sunnah_total": {"type": "int", "range": (0, 7), "section": "Spiritual"},
    "prayers": {"type": "int", "range": (0, 35), "section": "Spiritual"},
}


def calculate_daily_note_path(vault_path: str, date: datetime.date) -> Path:
    """
    Calculate the file path for a daily note.

    Args:
        vault_path: Path to the Obsidian vault
        date: Date for the daily note

    Returns:
        Path to the daily note file

    Example:
        >>> calculate_daily_note_path("/vault", datetime.date(2026, 1, 30))
        Path("/vault/01 - Journal/Daily/2026/01-January/2026-01-30.md")
    """
    year = str(date.year)
    month_str: str = date.strftime("%m-%B")  # "01-January"
    date_str: str = date.strftime("%Y-%m-%d")  # "2026-01-30"

    return Path(vault_path) / DAILY_JOURNAL_PATH / year / month_str / f"{date_str}.md"


def calculate_weekly_note_path(vault_path: str, date: datetime.date) -> Path:
    """
    Calculate the file path for a weekly note.

    Args:
        vault_path: Path to the Obsidian vault
        date: Any date within the target week

    Returns:
        Path to the weekly note file

    Example:
        >>> calculate_weekly_note_path("/vault", datetime.date(2026, 1, 30))
        Path("/vault/01 - Journal/Weekly/2026/2026-W05.md")
    """
    iso_year, iso_week, _ = date.isocalendar()
    week_str: str = f"{iso_year}-W{iso_week:02d}"  # "2026-W05"

    return Path(vault_path) / WEEKLY_JOURNAL_PATH / str(iso_year) / f"{week_str}.md"


def parse_frontmatter(file_path: Path) -> tuple[dict, str]:
    """
    Parse YAML frontmatter from a markdown file.

    Args:
        file_path: Path to the markdown file

    Returns:
        Tuple of (frontmatter_dict, remaining_content)
        Returns ({}, "") if file doesn't exist or has no frontmatter

    Example:
        >>> frontmatter, content = parse_frontmatter(Path("note.md"))
        >>> frontmatter["mood"]
        5
    """
    if not file_path.exists():
        return {}, ""

    try:
        content: str = file_path.read_text(encoding="utf-8")
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return {}, ""

    # Check for frontmatter
    if not content.startswith("---"):
        return {}, content

    # Split on second --- delimiter
    parts: list[str] = content.split("---", 2)
    if len(parts) < 3:
        return {}, content

    yaml_str: str = parts[1]
    remaining: str = parts[2]

    try:
        frontmatter = yaml.safe_load(yaml_str) or {}
        return frontmatter, remaining
    except yaml.YAMLError as e:
        print(f"Error parsing YAML frontmatter: {e}")
        return {}, content


def update_frontmatter(file_path: Path, updates: dict) -> bool:
    """
    Update specific frontmatter fields in a markdown file.

    Args:
        file_path: Path to the markdown file
        updates: Dictionary of field updates

    Returns:
        True if successful, False otherwise

    Example:
        >>> update_frontmatter(Path("note.md"), {"mood": 8, "book": "Dune"})
        True
    """
    if not file_path.exists():
        print(f"File does not exist: {file_path}")
        return False

    try:
        # Parse existing frontmatter
        frontmatter, content = parse_frontmatter(file_path)

        # Update fields
        for key, value in updates.items():
            frontmatter[key] = value

        # Reconstruct file
        yaml_str: str = yaml.dump(
            frontmatter, default_flow_style=False, allow_unicode=True, sort_keys=False
        )

        # Remove trailing newline from yaml.dump() output to avoid double newlines
        yaml_str = yaml_str.rstrip("\n")

        new_content: str = f"---\n{yaml_str}\n---{content}"

        # Write back to file
        file_path.write_text(new_content, encoding="utf-8")
        return True
    except Exception as e:
        print(f"Error updating frontmatter: {e}")
        return False


def validate_field_value(field_name: str, value: any, note_type: str) -> Optional[str]:
    """
    Validate a field value against its schema.

    Args:
        field_name: Name of the field
        value: Value to validate
        note_type: "daily" or "weekly"

    Returns:
        Error message if validation fails, None if valid

    Example:
        >>> validate_field_value("morning_mood", 15, "daily")
        "morning_mood must be between 1 and 10"
    """
    fields = DAILY_FIELDS if note_type == "daily" else WEEKLY_FIELDS

    if field_name not in fields:
        return None  # Unknown fields are allowed

    field_config = fields[field_name]
    field_type = field_config["type"]

    if field_type == "int":
        if value == "" or value is None:
            return None  # Empty values are allowed
        try:
            int_value = int(value)
            min_val, max_val = field_config["range"]
            if not (min_val <= int_value <= max_val):
                return f"{field_name} must be between {min_val} and {max_val}"
        except (ValueError, TypeError):
            return f"{field_name} must be a number"
    elif field_type == "float":
        if value == "" or value is None:
            return None  # Empty values are allowed
        try:
            float_value = float(value)
            min_val, max_val = field_config["range"]
            if not (min_val <= float_value <= max_val):
                return f"{field_name} must be between {min_val} and {max_val}"
        except (ValueError, TypeError):
            return f"{field_name} must be a number"
    elif field_type == "bool":
        if not isinstance(value, bool):
            return f"{field_name} must be true or false"

    return None


def get_fields_by_section(note_type: str) -> dict[str, list[str]]:
    """
    Get fields organized by section.

    Args:
        note_type: "daily" or "weekly"

    Returns:
        Dictionary mapping section names to lists of field names

    Example:
        >>> sections = get_fields_by_section("daily")
        >>> sections["Mood"]
        ["morning_mood", "evening_mood"]
    """
    fields = DAILY_FIELDS if note_type == "daily" else WEEKLY_FIELDS
    sections = {}

    for field_name, field_config in fields.items():
        section = field_config["section"]
        if section not in sections:
            sections[section] = []
        sections[section].append(field_name)

    return sections
