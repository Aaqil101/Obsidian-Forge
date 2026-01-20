# ----- Utils Modules-----
from src.utils import THEME_BG_SECONDARY, THEME_BORDER, THEME_TEXT_SECONDARY


def qss() -> str:
    return f"""
    /* === Splitter === */
    QSplitter::handle {{
        background-color: #444444;
        width: 3px;
        height: 3px;
    }}

    /* === Status Bar === */
    QStatusBar {{
        background-color: {THEME_BG_SECONDARY};
        color: {THEME_TEXT_SECONDARY};
        border-top: 1px solid {THEME_BORDER};
    }}
    """
