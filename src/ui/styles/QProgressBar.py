# ----- Core Modules-----
from src.core import BORDER_RADIUS_SMALL

# ----- Utils Modules-----
from src.utils import COLOR_DARK_BLUE, THEME_BORDER, THEME_TEXT_PRIMARY


def qss() -> str:
    return f"""
    /* === Progress Bar === */
    QProgressBar {{
        background-color: rgba(255, 255, 255, 0.04);
        border: 1px solid {THEME_BORDER};
        border-radius: {BORDER_RADIUS_SMALL}px;
        text-align: center;
        color: {THEME_TEXT_PRIMARY};
        height: 20px;
    }}

    QProgressBar::chunk {{
        background-color: {COLOR_DARK_BLUE};
        border-radius: 5px;
    }}
    """
