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
        background-color: #1F1F1F;
        color: {THEME_TEXT_PRIMARY};
        border: 1px solid #323232;
        border-radius: 0px;
        padding: 0px;
    }}
    QMenu::item {{
        color: {THEME_TEXT_PRIMARY};
        border-radius: 0px;
        padding: 2px 8px;
        min-height: 16px;
    }}
    QMenu::item::selected {{
        color: {THEME_TEXT_PRIMARY};
        background-color: #5076B2;
        border-radius: 0px;
    }}
    QMenu::icon {{
        margin: 3px;
    }}
    QMenu::item:disabled {{
        color: #828282;
    }}
    QMenu::separator {{
        background-color: #616161;
        border: none;
        height: 1px;
        margin: 0px 4px 0px 4px;
    }}
    """
