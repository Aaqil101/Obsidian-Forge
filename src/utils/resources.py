"""
Resource management for Obsidian Forge application.
Handles loading of icons and assets with PyInstaller support.
"""

# ----- Built-In Modules-----
import sys
from pathlib import Path

# ----- PySide6 Modules-----
from PySide6.QtGui import QIcon, QPixmap


def get_resource_path(relative_path: str) -> Path:
    """
    Get absolute path to resource, works for dev and for PyInstaller.

    Args:
        relative_path: Relative path to resource (e.g., 'assets/icon.png')

    Returns:
        Absolute Path to resource
    """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = Path(sys._MEIPASS)
    except AttributeError:
        # Not running as bundled app, use source directory
        # Get the project root (two levels up from this file)
        base_path: Path = Path(__file__).parent.parent.parent

    return base_path / relative_path


def get_icon(icon_name: str) -> QIcon:
    """
    Load an icon from the assets directory.

    Args:
        icon_name: Icon filename (e.g., 'obsidian-forge.ico')

    Returns:
        QIcon object
    """
    icon_path: Path = get_resource_path(f"assets/{icon_name}")
    icon = QIcon(str(icon_path))
    if icon.isNull():
        print(f"Warning: Icon not found: {icon_path}")
    return icon


def get_pixmap(image_name: str) -> QPixmap:
    """
    Load a pixmap from the assets directory.

    Args:
        image_name: Image filename (e.g., 'icon.png')

    Returns:
        QPixmap object
    """
    image_path: Path = get_resource_path(f"assets/{image_name}")
    pixmap = QPixmap(str(image_path))
    if pixmap.isNull():
        print(f"Warning: Pixmap not found: {image_path}")
    return pixmap


class Resources:
    """Static resource manager for backwards compatibility."""

    @staticmethod
    def icon(name: str) -> QIcon:
        """Load an icon from assets."""
        return get_icon(name)

    @staticmethod
    def pixmap(name: str) -> QPixmap:
        """Load a pixmap from assets."""
        return get_pixmap(name)
