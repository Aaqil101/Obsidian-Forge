"""
Reusable UI component factories for Obsidian Forge.
Following GitUI's component-based design pattern.
"""

# ----- PySide6 Modules -----
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QWidget

# ----- Core Modules -----
from src.core import (
    FONT_FAMILY,
    FONT_SIZE_HEADER,
    FONT_SIZE_LABEL,
    FONT_SIZE_SMALL,
    FONT_SIZE_TEXT,
    SPACING_SMALL,
)

# ----- Utils Modules-----
from src.utils import COLOR_LIGHT_BLUE, THEME_TEXT_SECONDARY


def create_header_label(text: str, size: int = None) -> QLabel:
    """
    Create a header label with Tokyo Night styling.

    Args:
        text: Label text
        size: Font size (defaults to Config.FONT_SIZE_HEADER)

    Returns:
        Configured QLabel
    """
    if size is None:
        size = FONT_SIZE_HEADER

    label = QLabel(text)
    font = QFont(FONT_FAMILY, size)
    font.setBold(True)
    font.setWeight(QFont.Weight.Bold)
    label.setFont(font)
    label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    return label


def create_subtitle_label(text: str) -> QLabel:
    """
    Create a subtitle label with Tokyo Night styling.

    Args:
        text: Label text

    Returns:
        Configured QLabel
    """
    label = QLabel(text)
    font = QFont(FONT_FAMILY, FONT_SIZE_SMALL)
    label.setFont(font)
    label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    label.setStyleSheet(f"color: {THEME_TEXT_SECONDARY};")
    return label


def create_info_label(text: str) -> QLabel:
    """
    Create an info box label with Tokyo Night styling.

    Args:
        text: Label text

    Returns:
        Configured QLabel with InfoBox property
    """
    label = QLabel(text)
    label.setProperty("InfoBox", True)
    label.setWordWrap(True)
    return label


def create_icon_label(icon_text: str, text: str = None, size: int = None) -> QLabel:
    """
    Create a label with Nerd Font icon.

    Args:
        icon_text: Nerd Font icon character
        text: Optional text to display after icon
        size: Font size (defaults to Config.FONT_SIZE_TEXT)

    Returns:
        Configured QLabel with icon
    """
    if size is None:
        size = FONT_SIZE_TEXT

    if text:
        display_text: str = f"{icon_text}  {text}"
    else:
        display_text = icon_text

    label = QLabel(display_text)
    font = QFont(FONT_FAMILY, size)
    label.setFont(font)
    return label


def create_primary_button(text: str, icon: str = None) -> QPushButton:
    """
    Create a primary action button.

    Args:
        text: Button text
        icon: Optional Nerd Font icon

    Returns:
        Configured QPushButton
    """
    if icon:
        display_text: str = f"{icon}  {text}"
    else:
        display_text = text

    button = QPushButton(display_text)
    button.setDefault(True)
    return button


def create_secondary_button(text: str, icon: str = None) -> QPushButton:
    """
    Create a secondary action button.

    Args:
        text: Button text
        icon: Optional Nerd Font icon

    Returns:
        Configured QPushButton
    """
    if icon:
        display_text: str = f"{icon}  {text}"
    else:
        display_text = text

    button = QPushButton(display_text)
    return button


def create_icon_button(icon: str, tooltip: str = None) -> QPushButton:
    """
    Create an icon-only button.

    Args:
        icon: Nerd Font icon character
        tooltip: Optional tooltip text

    Returns:
        Configured QPushButton
    """
    button = QPushButton(icon)
    if tooltip:
        button.setToolTip(tooltip)
    button.setFixedSize(40, 40)
    return button


def create_button_row(*buttons, spacing: int = None) -> QWidget:
    """
    Create a horizontal row of buttons.

    Args:
        *buttons: Variable number of QPushButton widgets
        spacing: Spacing between buttons (defaults to Config.SPACING_SMALL)

    Returns:
        QWidget containing the button row
    """
    if spacing is None:
        spacing = SPACING_SMALL

    widget = QWidget()
    layout = QHBoxLayout()
    layout.setSpacing(spacing)
    layout.addStretch()

    for button in buttons:
        layout.addWidget(button)

    widget.setLayout(layout)
    return widget


def create_stat_label(icon: str, value: str, label: str = None) -> QWidget:
    """
    Create a statistic display widget with icon, value, and optional label.

    Args:
        icon: Nerd Font icon character
        value: Statistic value
        label: Optional label text

    Returns:
        QWidget containing the statistic display
    """
    widget = QWidget()
    layout = QHBoxLayout()
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(8)

    # Icon
    icon_label = QLabel(icon)
    icon_font = QFont(FONT_FAMILY, FONT_SIZE_HEADER)
    icon_label.setFont(icon_font)
    icon_label.setStyleSheet(f"color: {COLOR_LIGHT_BLUE};")
    layout.addWidget(icon_label)

    # Value
    value_label = QLabel(value)
    value_font = QFont(FONT_FAMILY, FONT_SIZE_LABEL)
    value_font.setBold(True)
    value_label.setFont(value_font)
    layout.addWidget(value_label)

    # Optional label
    if label:
        label_widget = QLabel(label)
        label_font = QFont(FONT_FAMILY, FONT_SIZE_SMALL)
        label_widget.setFont(label_font)
        label_widget.setStyleSheet(f"color: {THEME_TEXT_SECONDARY};")
        layout.addWidget(label_widget)

    layout.addStretch()
    widget.setLayout(layout)
    return widget


def create_section_header(text: str) -> QLabel:
    """
    Create a section header label.

    Args:
        text: Header text

    Returns:
        Configured QLabel
    """
    label = QLabel(text)
    font = QFont(FONT_FAMILY, FONT_SIZE_LABEL)
    font.setBold(True)
    label.setFont(font)
    label.setStyleSheet(f"color: {COLOR_LIGHT_BLUE};")
    return label
