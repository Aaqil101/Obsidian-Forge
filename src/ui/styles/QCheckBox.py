# ----- Core Modules-----
from src.core import BORDER_RADIUS_SMALL

# ----- Utils Modules-----
from src.utils import (
    COLOR_DARK_BLUE,
    COLOR_LIGHT_BLUE,
    THEME_BORDER,
    THEME_TEXT_PRIMARY,
)


def qss() -> str:
    return f"""
    /* === Check Box === */
    QCheckBox {{
        color: {THEME_TEXT_PRIMARY};
        spacing: 8px;
    }}

    QCheckBox::indicator {{
        width: 18px;
        height: 18px;
        border: 2px solid {THEME_BORDER};
        border-radius: {BORDER_RADIUS_SMALL - 2}px;
        background-color: rgba(255, 255, 255, 0.04);
    }}

    QCheckBox::indicator:hover {{
        border: 2px solid rgba(122, 162, 247, 0.5);
        background-color: rgba(255, 255, 255, 0.06);
    }}

    QCheckBox::indicator:checked {{
        background-color: {COLOR_DARK_BLUE};
        border: 2px solid {COLOR_DARK_BLUE};
    }}

    QCheckBox::indicator:checked:hover {{
        background-color: {COLOR_LIGHT_BLUE};
        border: 2px solid {COLOR_LIGHT_BLUE};
    }}

    QCheckBox::indicator:disabled {{
        background-color: rgba(255, 255, 255, 0.02);
        border: 2px solid rgba(255, 255, 255, 0.1);
    }}
    """
