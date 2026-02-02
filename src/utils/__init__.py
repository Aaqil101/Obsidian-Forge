"""Utility modules for Obsidian Forge application."""

from src.utils.autostart import (
    disable_autostart,
    enable_autostart,
    is_autostart_enabled,
)
from src.utils.color import (
    COLOR_COMPLETE,
    COLOR_CYAN,
    COLOR_DARK_BLUE,
    COLOR_FAILED,
    COLOR_GREEN,
    COLOR_LIGHT_BLUE,
    COLOR_ORANGE,
    COLOR_PENDING,
    COLOR_PURPLE,
    COLOR_QUEUED,
    COLOR_RED,
    COLOR_SCANNING,
    COLOR_SUCCESS,
    COLOR_YELLOW,
    THEME_BG_PRIMARY,
    THEME_BG_SECONDARY,
    THEME_BORDER,
    THEME_TEXT_PRIMARY,
    THEME_TEXT_SECONDARY,
    AccentTheme,
)
from src.utils.hover_button import HoverIconButtonSVG
from src.utils.icons import Icons
from src.utils.resources import get_icon

__all__: list[str] = [
    "Icons",
    "get_icon",
    "HoverIconButtonSVG",
    "enable_autostart",
    "disable_autostart",
    "is_autostart_enabled",
    "COLOR_COMPLETE",
    "COLOR_CYAN",
    "COLOR_DARK_BLUE",
    "COLOR_FAILED",
    "COLOR_GREEN",
    "COLOR_LIGHT_BLUE",
    "COLOR_ORANGE",
    "COLOR_PENDING",
    "COLOR_PURPLE",
    "COLOR_QUEUED",
    "COLOR_RED",
    "COLOR_SCANNING",
    "COLOR_SUCCESS",
    "COLOR_YELLOW",
    "THEME_BG_PRIMARY",
    "THEME_BG_SECONDARY",
    "THEME_BORDER",
    "THEME_TEXT_PRIMARY",
    "THEME_TEXT_SECONDARY",
    "AccentTheme",
]
