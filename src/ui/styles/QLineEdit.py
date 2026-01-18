# ----- Core Modules-----
from src.core import BORDER_RADIUS_SMALL, FONT_SIZE_SMALL

# ----- Utils Modules-----
from src.utils import COLOR_DARK_BLUE, THEME_BORDER, THEME_TEXT_PRIMARY


def qss() -> str:
    return f"""
    /* === Line Edit === */
    QLineEdit {{
        background-color: rgba(255, 255, 255, 0.04);
        color: {THEME_TEXT_PRIMARY};
        border-radius: 4px;
        padding: 6px 10px;
        border: 2px solid transparent;
    }}
    QLineEdit:focus {{
        background-color: #222;
        border-bottom: 2px solid {COLOR_DARK_BLUE};
        border-right: 2px solid {COLOR_DARK_BLUE};
        font-style: unset;
    }}

    /* === Search Bar === */
    QLineEdit[SearchBar="true"] {{
        background-color: rgba(255, 255, 255, 0.04);
        color: {THEME_TEXT_PRIMARY};
        border: 1px solid {THEME_BORDER};
        border-radius: {BORDER_RADIUS_SMALL}px;
        padding: 6px 8px 6px 0px;
        font-size: {FONT_SIZE_SMALL}pt;
    }}

    QLineEdit[SearchBar="true"]:focus {{
        background-color: rgba(255, 255, 255, 0.06);
        border: 1px solid {COLOR_DARK_BLUE};
    }}
    """
