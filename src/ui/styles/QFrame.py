# ----- Core Modules-----
from src.core import BORDER_RADIUS_SMALL

# ----- Utils Modules-----
from src.utils import COLOR_DARK_BLUE, THEME_BG_SECONDARY, THEME_BORDER


def qss() -> str:
    return f"""
    /* === Script Card === */
    QFrame[ScriptCard="true"] {{
        background-color: rgba(255, 255, 255, 0.03);
        border: 1px solid {THEME_BORDER};
        border-radius: {BORDER_RADIUS_SMALL}px;
    }}

    QFrame[ScriptCard="true"]:hover {{
        background-color: rgba(122, 162, 247, 0.1);
        border: 1px solid {COLOR_DARK_BLUE};
    }}

    /* === Settings Group (Collapsible Section) === */
    QFrame[SettingsGroup="true"] {{
        background-color: {THEME_BG_SECONDARY};
        border: 1px solid {THEME_BORDER};
        border-radius: {BORDER_RADIUS_SMALL}px;
        padding: 8px;
        margin-bottom: 8px;
    }}
    """
