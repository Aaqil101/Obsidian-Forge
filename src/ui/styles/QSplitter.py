# ----- Utils Modules-----
from src.utils import (
    COLOR_DARK_BLUE,
    THEME_BG_SECONDARY,
    THEME_BORDER,
    THEME_TEXT_SECONDARY,
)


def qss() -> str:
    return f"""
    /* === Splitter === */
    QSplitter::handle {{
        background-color: {THEME_BORDER};
        width: 2px;
    }}

    QSplitter::handle:hover {{
        background-color: {COLOR_DARK_BLUE};
    }}

    /* === Status Bar === */
    QStatusBar {{
        background-color: {THEME_BG_SECONDARY};
        color: {THEME_TEXT_SECONDARY};
        border-top: 1px solid {THEME_BORDER};
    }}
    """
