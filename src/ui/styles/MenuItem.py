# ----- Core Modules-----
from src.core import BORDER_RADIUS_SMALL, FONT_SIZE_SMALL

# ----- Utils Modules-----
from src.utils import THEME_TEXT_PRIMARY, THEME_TEXT_SUBTLE


def qss() -> str:
    return f"""
    /* === Custom Menu Items === */
    #MenuItem {{
        background-color: transparent;
        border-radius: {BORDER_RADIUS_SMALL}px;
        min-width: 120px;
    }}

    #MenuItem:hover {{
        background-color: rgba(122, 162, 247, 0.15);
    }}

    #MenuItemText {{
        background-color: transparent;
        color: {THEME_TEXT_PRIMARY};
    }}

    #MenuItemShortcut {{
        background-color: transparent;
        color: {THEME_TEXT_SUBTLE};
        font-size: {FONT_SIZE_SMALL}pt;
    }}
    """
