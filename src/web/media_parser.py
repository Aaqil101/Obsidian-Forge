"""
Media aggregator that uses individual parsers for each media type.
This module provides a unified interface to get all media items from the vault.
"""

from pathlib import Path
from typing import Dict, List, Union
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.config import Config
from web.parsers import (
    Book,
    YouTubeVideo,
    Movie,
    TVShow,
    Documentary,
    scan_books_directory,
    scan_youtube_directory,
    scan_movies_directory,
    scan_tv_shows_directory,
    scan_documentaries_directory,
)

# Type alias for media items
MediaItem = Union[Book, YouTubeVideo, Movie, TVShow, Documentary]


def get_all_media_items(config: Config) -> Dict[str, List[MediaItem]]:
    """
    Get all media items from all configured directories using specialized parsers.

    Args:
        config: Config object with vault paths

    Returns:
        Dictionary mapping media type to list of media items
    """
    media_data = {
        "books": [],
        "youtube": [],
        "movies": [],
        "tv_shows": [],
        "documentaries": [],
    }

    # Scan each media directory using specialized parsers
    books_path = config.get_books_path()
    if books_path:
        media_data["books"] = scan_books_directory(books_path)

    youtube_path = config.get_youtube_path()
    if youtube_path:
        media_data["youtube"] = scan_youtube_directory(youtube_path)

    movies_path = config.get_movies_path()
    if movies_path:
        media_data["movies"] = scan_movies_directory(movies_path)

    tv_shows_path = config.get_tv_shows_path()
    if tv_shows_path:
        media_data["tv_shows"] = scan_tv_shows_directory(tv_shows_path)

    documentaries_path = config.get_documentaries_path()
    if documentaries_path:
        media_data["documentaries"] = scan_documentaries_directory(documentaries_path)

    return media_data


# For backward compatibility, keep the old function
def parse_media_file(file_path: Path, media_type: str) -> MediaItem:
    """
    Parse a media file using the appropriate parser.

    This function is kept for backward compatibility.

    Args:
        file_path: Path to the markdown file
        media_type: Type of media (books, movies, tv_shows, youtube, documentaries)

    Returns:
        Media item object or None if parsing fails
    """
    from web.parsers import (
        parse_book,
        parse_youtube_video,
        parse_movie,
        parse_tv_show,
        parse_documentary,
    )

    parsers = {
        "books": parse_book,
        "youtube": parse_youtube_video,
        "movies": parse_movie,
        "tv_shows": parse_tv_show,
        "documentaries": parse_documentary,
    }

    parser = parsers.get(media_type)
    if parser:
        return parser(file_path)
    return None
