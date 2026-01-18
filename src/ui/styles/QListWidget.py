# ----- Core Modules-----
from src.core import BORDER_RADIUS_SMALL

# ----- Utils Modules-----
from src.utils import THEME_TEXT_PRIMARY


def qss() -> str:
    return f"""
    /* === List Widget === */
    QListWidget {{
        background-color: rgba(255, 255, 255, 0.04);
        color: {THEME_TEXT_PRIMARY};
        border-radius: {BORDER_RADIUS_SMALL - 2}px;
        padding: 4px;
    }}
    QListWidget::item {{
        padding: 6px;
        border-radius: {BORDER_RADIUS_SMALL - 3}px;
    }}
    QListWidget::item:selected {{
        background-color: rgba(122, 162, 247, 0.3);
    }}
    QListWidget::item:hover {{
        color: {THEME_TEXT_PRIMARY};
        background-color: rgba(255, 255, 255, 0.06);
    }}
    QListWidget::item:selected:!active {{
        color: {THEME_TEXT_PRIMARY};
        background: rgba(255, 255, 255, 0.08);
    }}
    QListWidget:focus {{
        color: {THEME_TEXT_PRIMARY};
        background-color: rgba(255, 255, 255, 0.06);
        outline: none;
    }}
    """
