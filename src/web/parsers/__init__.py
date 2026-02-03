"""
Media parsers package for parsing different types of media from Obsidian vault.
"""

from .books_parser import Book, parse_book, scan_books_directory
from .youtube_parser import YouTubeVideo, parse_youtube_video, scan_youtube_directory
from .movies_parser import Movie, parse_movie, scan_movies_directory
from .tv_shows_parser import TVShow, parse_tv_show, scan_tv_shows_directory
from .documentaries_parser import Documentary, parse_documentary, scan_documentaries_directory

__all__ = [
    "Book",
    "YouTubeVideo",
    "Movie",
    "TVShow",
    "Documentary",
    "parse_book",
    "scan_books_directory",
    "parse_youtube_video",
    "scan_youtube_directory",
    "parse_movie",
    "scan_movies_directory",
    "parse_tv_show",
    "scan_tv_shows_directory",
    "parse_documentary",
    "scan_documentaries_directory",
]
