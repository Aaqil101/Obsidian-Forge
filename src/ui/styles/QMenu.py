# ----- Core Modules-----
from src.core import BORDER_RADIUS, BORDER_RADIUS_SMALL

# ----- Utils Modules-----
from src.utils import (
    THEME_BG_SECONDARY,
    THEME_BORDER,
    THEME_TEXT_PRIMARY,
    THEME_TEXT_SUBTLE,
)


def qss() -> str:
    return f"""
    /* === Menu === */
    QMenu {{
        background-color: {THEME_BG_SECONDARY};
        color: {THEME_TEXT_PRIMARY};
        border: 1px solid {THEME_BORDER};
        border-radius: {BORDER_RADIUS}px;
        padding: 4px;
    }}

    QMenu::icon {{
        padding-left: 8px;
    }}

    QMenu::item {{
        padding: 6px 24px 6px 10px;
        border-radius: {BORDER_RADIUS_SMALL}px;
    }}

    QMenu::item:selected {{
        background-color: rgba(122, 162, 247, 0.2);
        color: #FFFFFF;
    }}

    QMenu::item:disabled {{
        color: {THEME_TEXT_SUBTLE};
    }}

    QMenu::separator {{
        height: 1px;
        background-color: {THEME_BORDER};
        margin: 4px 8px;
    }}
    """
