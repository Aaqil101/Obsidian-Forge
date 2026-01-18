# ----- Core Modules-----
from src.core import BORDER_RADIUS_SMALL

# ----- Utils Modules-----
from src.utils import THEME_TEXT_PRIMARY


def qss() -> str:
    return f"""
    /* === Script Row (Button Cards) === */
    QWidget[ScriptRow="true"] {{
        background-color: rgba(25, 30, 40,  0.6);
        border: 1px solid rgba(50, 60, 75, 0.6);
        border-radius: {BORDER_RADIUS_SMALL}px;
    }}

    QWidget[ScriptRow="true"]:hover {{
        background-color: rgba(35, 42, 55, 0.8);
        border: 1px solid rgba(80, 95, 115, 0.8);
    }}

    QWidget[ScriptRow="true"]:disabled {{
        background-color: rgba(20, 25, 35, 0.4);
        border: 1px solid rgba(40, 45, 55, 0.5);
        opacity: 0.5;
    }}

    QWidget[ScriptRow="true"] QLabel {{
        background: transparent;
        color: {THEME_TEXT_PRIMARY};
    }}
    """
