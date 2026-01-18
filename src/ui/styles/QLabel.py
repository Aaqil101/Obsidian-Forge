# ----- Core Modules-----
from src.core import BORDER_RADIUS_SMALL, FONT_SIZE_SMALL

# ----- Utils Modules-----
from src.utils import (
    COLOR_DARK_BLUE,
    COLOR_LIGHT_BLUE,
    THEME_BG_SECONDARY,
    THEME_BORDER,
    THEME_TEXT_PRIMARY,
    THEME_TEXT_SUBTLE,
)


def qss() -> str:
    return f"""
    /* === Labels === */
    QLabel {{
        color: {THEME_TEXT_PRIMARY};
        background-color: transparent;
    }}

    /* === Info Label === */
    QLabel[InfoBox="true"] {{
        background-color: {THEME_BG_SECONDARY};
        border: 1px solid {THEME_BORDER};
        border-left: 3px solid {COLOR_DARK_BLUE};
        border-radius: {BORDER_RADIUS_SMALL}px;
        padding: 12px;
        color: {THEME_TEXT_PRIMARY};
    }}

    QLabel[InfoLabel="true"] {{
        color: {THEME_TEXT_SUBTLE};
        font-size: {FONT_SIZE_SMALL}pt;
    }}

    /* === Card Title === */
    QLabel[CardTitle="true"] {{
        color: {THEME_TEXT_PRIMARY};
        font-size: 10pt;
        font-weight: bold;
        background-color: transparent;
    }}

    /* === Card Subtitle === */
    QLabel[CardSubtitle="true"] {{
        color: {THEME_TEXT_SUBTLE};
        font-size: {FONT_SIZE_SMALL}pt;
        background-color: transparent;
    }}

    /* === Section Header === */
    QLabel[SectionHeader="true"] {{
        color: {COLOR_LIGHT_BLUE};
        font-size: {FONT_SIZE_SMALL}pt;
        font-weight: bold;
        padding: 2px 4px 2px 4px;
    }}
    """
