"""
Resource management for Obsidian Forge application.
Handles loading of icons and assets with PyInstaller support.
"""

# ----- Built-In Modules-----
import re
import sys
from pathlib import Path

# ----- PySide6 Modules-----
from PySide6.QtCore import QByteArray, Qt
from PySide6.QtGui import QIcon, QPainter, QPixmap
from PySide6.QtSvg import QSvgRenderer


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


def get_icon(icon_name: str, color: str = None) -> QIcon:
    """
    Load an icon from the assets directory, optionally recoloring SVG icons.

    Args:
        icon_name: Icon filename (e.g., 'obsidian-forge.ico')
        color: Hex color to apply to SVG icons (e.g., '#c0caf5')

    Returns:
        QIcon object
    """
    icon_path: Path = get_resource_path(f"assets/{icon_name}")

    # If color is specified and it's an SVG, recolor it
    if color and icon_name.lower().endswith(".svg"):
        try:
            with open(icon_path, "r", encoding="utf-8") as f:
                svg_content = f.read()

            # Replace stroke color in SVG
            svg_content = re.sub(r'stroke="[^"]*"', f'stroke="{color}"', svg_content)
            # Replace fill color in SVG (if any)
            svg_content = re.sub(
                r'fill="(?!none)[^"]*"', f'fill="{color}"', svg_content
            )

            # Create icon from modified SVG
            byte_array = QByteArray(svg_content.encode("utf-8"))
            renderer = QSvgRenderer(byte_array)
            pixmap = QPixmap(24, 24)
            pixmap.fill(Qt.GlobalColor.transparent)  # Transparent background

            painter = QPainter(pixmap)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            renderer.render(painter)
            painter.end()

            return QIcon(pixmap)
        except Exception as e:
            print(f"Warning: Could not recolor SVG icon {icon_name}: {e}")

    # Default icon loading
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
