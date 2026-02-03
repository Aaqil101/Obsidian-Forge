"""
Books parser for reading markdown files from Obsidian vault.
Parses YAML frontmatter and extracts book metadata.
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
class Book:
    """Represents a book parsed from markdown."""

    id: str  # Filename without extension
    title: str
    media_type: str = "books"

    # Book-specific fields
    authors: Optional[str] = None  # Comma-separated author names (may include wiki links)
    categories: Optional[str] = None  # Comma-separated categories (may include wiki links)
    subtitle: Optional[str] = None
    publisher: Optional[str] = None
    publish: Optional[str] = None  # Publish date
    total_pages: Optional[int] = None
    book_url: Optional[str] = None
    cover: Optional[str] = None  # Cover URL
    localCover: Optional[str] = None  # Local cover image path
    isbn10: Optional[str] = None
    isbn13: Optional[str] = None

    # User tracking fields
    status: Optional[str] = None
    priority: Optional[str] = None
    start_reading: Optional[str] = None
    current_page: Optional[int] = None
    end_reading: Optional[str] = None
    complete: Optional[bool] = None
    rating: Optional[float] = None

    # Metadata
    year: Optional[int] = None
    created: Optional[str] = None
    metadata: Dict = field(default_factory=dict)  # Full frontmatter
    file_path: str = ""  # Path to markdown file


def parse_book(file_path: Path) -> Optional[Book]:
    """
    Parse a single markdown file and extract book metadata.

    Args:
        file_path: Path to the markdown file

    Returns:
        Book object or None if parsing fails
    """
    try:
        frontmatter, _ = parse_frontmatter(file_path)

        if not frontmatter:
            print(f"Warning: No frontmatter found in {file_path}")
            return None

        # Extract fields from frontmatter
        item_id = file_path.stem
        title = frontmatter.get("title", "")

        # Convert title to string if it's not already (YAML might parse it as a list)
        if isinstance(title, list):
            title = title[0] if title else ""
        title = str(title) if title else ""

        # Extract year from publish date
        publish = frontmatter.get("publish", "")
        year = None
        if publish:
            year = _extract_year(str(publish))

        # Handle empty titles
        if not title:
            title = item_id.replace("-", " ").replace("_", " ").title()

        # Clean authors field (keep as string, may contain wiki links)
        authors = frontmatter.get("authors")
        categories = frontmatter.get("categories")

        # Get cover image (prefer localCover over cover)
        cover_image = frontmatter.get("localCover") or frontmatter.get("cover")

        return Book(
            id=item_id,
            title=title,
            authors=authors,
            categories=categories,
            subtitle=frontmatter.get("subtitle"),
            publisher=frontmatter.get("publisher"),
            publish=publish,
            total_pages=_parse_number(frontmatter.get("total_pages"), int),
            book_url=frontmatter.get("book_url"),
            cover=frontmatter.get("cover"),
            localCover=frontmatter.get("localCover"),
            isbn10=frontmatter.get("isbn10"),
            isbn13=frontmatter.get("isbn13"),
            status=frontmatter.get("status"),
            priority=frontmatter.get("priority"),
            start_reading=frontmatter.get("start_reading"),
            current_page=_parse_number(frontmatter.get("current_page"), int),
            end_reading=frontmatter.get("end_reading"),
            complete=_parse_bool(frontmatter.get("complete")),
            rating=_parse_number(frontmatter.get("rating"), float),
            year=year,
            created=frontmatter.get("created"),
            metadata=frontmatter,
            file_path=str(file_path),
        )

    except Exception as e:
        print(f"Error parsing book {file_path}: {e}")
        return None


def scan_books_directory(directory: Path) -> List[Book]:
    """
    Scan directory for all book markdown files and parse them.

    Args:
        directory: Path to directory containing markdown files

    Returns:
        List of Book objects
    """
    books = []

    if not directory or not directory.exists():
        print(f"Books directory not found: {directory}")
        return books

    # Recursively find all .md files
    for md_file in directory.rglob("*.md"):
        book = parse_book(md_file)
        if book:
            books.append(book)

    print(f"Found {len(books)} books in {directory}")
    return books


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
