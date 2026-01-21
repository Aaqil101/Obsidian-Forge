# ----- Utils Modules-----
from src.utils import THEME_BG_SECONDARY


def qss() -> str:
    return f"""
    /* === Settings Group (Collapsible Section) === */
    QFrame[SettingsGroup="true"] {{
        background-color: {THEME_BG_SECONDARY};
        border: 1px solid #444444;
        padding: 4px;
        margin-bottom: 4px;
    }}
    """
