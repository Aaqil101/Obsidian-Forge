# ----- Utils Modules-----
from src.utils import THEME_BG_SECONDARY


def qss() -> str:
    return f"""
    /* === Widget === */
    QWidget[CardsContainer="true"] {{
        background: transparent;
    }}

    /* === Header Bar === */
    #HeaderBar {{
        background-color: {THEME_BG_SECONDARY};
    }}
    """
