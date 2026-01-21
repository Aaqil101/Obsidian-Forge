# ----- Utils Modules-----
from src.utils import COLOR_DARK_BLUE, THEME_TEXT_PRIMARY


def qss() -> str:
    return f"""
    /* === Line Edit === */
    QLineEdit {{
        background-color: rgba(255, 255, 255, 0.04);
        color: {THEME_TEXT_PRIMARY};
        border-radius: 4px;
        padding: 6px 10px;
        border: 2px solid transparent;
    }}
    QLineEdit:focus {{
        background-color: #222;
        border-bottom: 2px solid {COLOR_DARK_BLUE};
        border-right: 2px solid {COLOR_DARK_BLUE};
        font-style: unset;
    }}

    /* === Search Bar === */
    QLineEdit[SearchBar="true"] {{
        background-color: rgba(255, 255, 255, 0.04);
        color: {THEME_TEXT_PRIMARY};
        border: 1px solid #444444;
        border-radius: 0px;
        padding: 1px;
    }}
    QLineEdit[SearchBar="true"]:hover {{
        background-color: rgba(255, 255, 255, 0.06);
        border: 1px solid #555555;
    }}
    QLineEdit[SearchBar="true"]:focus {{
        background-color: #222;
        border: 1px solid {COLOR_DARK_BLUE};
    }}
    """
