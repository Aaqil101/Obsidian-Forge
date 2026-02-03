"""
YouTube video parser for reading markdown files from Obsidian vault.
Parses YAML frontmatter and extracts YouTube video metadata.
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
class YouTubeVideo:
    """Represents a YouTube video parsed from markdown."""

    id: str  # Filename without extension
    title: str
    media_type: str = "youtube"

    # YouTube-specific fields
    author: Optional[str] = None  # Channel name
    subscribers: Optional[str] = None
    length: Optional[str] = None
    publish_date: Optional[str] = None
    thumbnail: Optional[str] = None  # Wiki link
    thumbnail_url: Optional[str] = None  # Direct URL
    description: Optional[str] = None
    youtube_url: Optional[str] = None

    # User tracking fields
    category: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    rewatch: Optional[bool] = None
    last_watch: Optional[str] = None
    complete: Optional[bool] = None
    like: Optional[bool] = None
    rating: Optional[float] = None

    # Metadata
    year: Optional[int] = None
    created: Optional[str] = None
    metadata: Dict = field(default_factory=dict)  # Full frontmatter
    file_path: str = ""  # Path to markdown file


def parse_youtube_video(file_path: Path) -> Optional[YouTubeVideo]:
    """
    Parse a single markdown file and extract YouTube video metadata.

    Args:
        file_path: Path to the markdown file

    Returns:
        YouTubeVideo object or None if parsing fails
    """
    try:
        frontmatter, _ = parse_frontmatter(file_path)

        if not frontmatter:
            print(f"Warning: No frontmatter found in {file_path}")
            return None

        # Extract fields from frontmatter
        item_id = file_path.stem
        title = frontmatter.get("aliases", "")

        # Convert title to string if it's not already (YAML might parse it as a list)
        if isinstance(title, list):
            title = title[0] if title else ""
        title = str(title) if title else ""

        # Extract year from publish_date
        publish_date = frontmatter.get("publish_date", "")
        year = None
        if publish_date:
            year = _extract_year(str(publish_date))

        # Handle empty titles
        if not title:
            title = item_id.replace("-", " ").replace("_", " ").title()

        # Clean author field (remove wiki link brackets if present)
        author = frontmatter.get("author", "")
        if author:
            # Convert to string if it's not already (YAML might parse it as a list)
            author = str(author) if not isinstance(author, str) else author
            # Remove wiki link brackets if present
            if author.startswith("[[") and author.endswith("]]"):
                author = author[2:-2]

        return YouTubeVideo(
            id=item_id,
            title=title,
            author=author,
            subscribers=frontmatter.get("subscribers"),
            length=frontmatter.get("length"),
            publish_date=publish_date,
            thumbnail=frontmatter.get("thumbnail"),
            thumbnail_url=frontmatter.get("thumbnail_url"),
            description=frontmatter.get("description"),
            youtube_url=frontmatter.get("youtube_url"),
            category=frontmatter.get("category"),
            status=frontmatter.get("status"),
            priority=frontmatter.get("priority"),
            rewatch=_parse_bool(frontmatter.get("rewatch")),
            last_watch=frontmatter.get("last_watch"),
            complete=_parse_bool(frontmatter.get("complete")),
            like=_parse_bool(frontmatter.get("like")),
            rating=_parse_number(frontmatter.get("rating"), float),
            year=year,
            created=frontmatter.get("created"),
            metadata=frontmatter,
            file_path=str(file_path),
        )

    except Exception as e:
        print(f"Error parsing YouTube video {file_path}: {e}")
        return None


def scan_youtube_directory(directory: Path) -> List[YouTubeVideo]:
    """
    Scan directory for all YouTube video markdown files and parse them.

    Args:
        directory: Path to directory containing markdown files

    Returns:
        List of YouTubeVideo objects
    """
    videos = []

    if not directory or not directory.exists():
        print(f"YouTube directory not found: {directory}")
        return videos

    # Recursively find all .md files
    for md_file in directory.rglob("*.md"):
        video = parse_youtube_video(md_file)
        if video:
            videos.append(video)

    print(f"Found {len(videos)} YouTube videos in {directory}")
    return videos


def _parse_number(value, num_type):
    """Safely parse a number from a value."""
    if value is None or value == "":
        return None
    try:
        return num_type(value)
    except (ValueError, TypeError):
        return None


def _parse_bool(value) -> Optional[bool]:
    """Safely parse a boolean from a value."""
    if value is None or value == "":
        return None
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() in ("true", "yes", "1")
    return bool(value)


def _extract_year(date_string: str) -> Optional[int]:
    """Extract year from a date string."""
    if not date_string:
        return None

    # Try to find a 4-digit year
    match = re.search(r"\b(19|20)\d{2}\b", date_string)
    if match:
        return int(match.group())

    return None
