# ----- Utils Modules-----
from src.utils import THEME_BG_SECONDARY, AccentTheme


def qss() -> str:
    # Get the app's accent color theme
    accent: dict[str, str] = AccentTheme.get()

    return f"""
    /* === Widget === */
    QWidget[CardsContainer="true"] {{
        background: transparent;
    }}

    /* === Header Bar === */
    #HeaderBar {{
        background-color: {THEME_BG_SECONDARY};
    }}

    /* === Search Container === */
    #SearchContainer {{
        background-color: {THEME_BG_SECONDARY};
        border: 1px solid {accent['border']};
        border-radius: 0px;
    }}
    """
