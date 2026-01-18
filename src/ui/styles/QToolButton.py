# ----- Core Modules-----
from src.core import BORDER_RADIUS_SMALL


def qss() -> str:
    return f"""
    /* === Tool Button === */
    QToolButton {{
        background-color: transparent;
        border: none;
        border-radius: {BORDER_RADIUS_SMALL}px;
        padding: 4px;
    }}

    QToolButton:hover {{
        background-color: rgba(122, 162, 247, 0.15);
    }}

    QToolButton:pressed {{
        background-color: rgba(122, 162, 247, 0.25);
    }}
    """
