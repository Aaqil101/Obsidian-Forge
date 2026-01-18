# ----- Utils Modules-----
from src.utils import COLOR_DARK_BLUE, COLOR_LIGHT_BLUE, THEME_TEXT_PRIMARY


def qss() -> str:
    return f"""
    /* === Text Edit === */
    QTextEdit {{
        background-color: rgba(255, 255, 255, 0.04);
        color: {THEME_TEXT_PRIMARY};
        border-radius: 4px;
        padding: 8px;
        selection-background-color: {COLOR_LIGHT_BLUE};
    }}

    QTextEdit:focus {{
        background-color: #222;
        border-bottom: 2px solid {COLOR_DARK_BLUE};
        border-right: 2px solid {COLOR_DARK_BLUE};
        font-style: unset;
    }}
    """
