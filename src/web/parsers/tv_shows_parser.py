"""
TV Shows parser for reading markdown files from Obsidian vault.
Parses YAML frontmatter and extracts TV show metadata.

TODO: Update this parser with the actual TV show template structure when available.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional
import sys
import re

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.frontmatter_handler import parse_frontmatter


@dataclass
class TVShow:
    """Represents a TV show parsed from markdown."""

    id: str  # Filename without extension
    title: str
    media_type: str = "tv_shows"

    # TV show-specific fields (based on current implementation)
    poster: Optional[str] = None  # Poster image URL
    scoreImdb: Optional[str] = None  # IMDB score (e.g., "8.5/10")
    rating: Optional[float] = None  # Parsed numeric rating
    status: Optional[str] = None
    year: Optional[int] = None

    # Metadata
    created: Optional[str] = None
    metadata: Dict = field(default_factory=dict)  # Full frontmatter
    file_path: str = ""  # Path to markdown file


def parse_tv_show(file_path: Path) -> Optional[TVShow]:
    """
    Parse a single markdown file and extract TV show metadata.

    Args:
        file_path: Path to the markdown file

    Returns:
        TVShow object or None if parsing fails
    """
    try:
        frontmatter, _ = parse_frontmatter(file_path)

        if not frontmatter:
            print(f"Warning: No frontmatter found in {file_path}")
            return None

        # Extract fields from frontmatter
        item_id = file_path.stem
        title = frontmatter.get("Title", "")

        # Convert title to string if it's not already (YAML might parse it as a list)
        if isinstance(title, list):
            title = title[0] if title else ""
        title = str(title) if title else ""

        # Parse IMDB rating (usually formatted as "8.5/10")
        score_imdb = frontmatter.get("scoreImdb", "")
        rating = None
        if score_imdb:
            rating = _parse_number(str(score_imdb).split("/")[0], float)

        # Handle empty titles
        if not title:
            title = item_id.replace("-", " ").replace("_", " ").title()

        return TVShow(
            id=item_id,
            title=title,
            poster=frontmatter.get("poster"),
            scoreImdb=score_imdb,
            rating=rating,
            status=frontmatter.get("status"),
            year=_parse_number(frontmatter.get("Year"), int),
            created=frontmatter.get("created"),
            metadata=frontmatter,
            file_path=str(file_path),
        )

    except Exception as e:
        print(f"Error parsing TV show {file_path}: {e}")
        return None


def scan_tv_shows_directory(directory: Path) -> List[TVShow]:
    """
    Scan directory for all TV show markdown files and parse them.

    Args:
        directory: Path to directory containing markdown files

    Returns:
        List of TVShow objects
    """
    tv_shows = []

    if not directory or not directory.exists():
        print(f"TV shows directory not found: {directory}")
        return tv_shows

    # Recursively find all .md files
    for md_file in directory.rglob("*.md"):
        tv_show = parse_tv_show(md_file)
        if tv_show:
            tv_shows.append(tv_show)

    print(f"Found {len(tv_shows)} TV shows in {directory}")
    return tv_shows


def _parse_number(value, num_type):
    """Safely parse a number from a value."""
    if value is None or value == "":
        return None
    try:
        return num_type(value)
    except (ValueError, TypeError):
        return None


def _extract_year(date_string: str) -> Optional[int]:
    """Extract year from a date string."""
    if not date_string:
        return None

    # Try to find a 4-digit year
    match = re.search(r"\b(19|20)\d{2}\b", date_string)
    if match:
        return int(match.group())

    return None
