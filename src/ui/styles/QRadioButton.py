# ----- Utils Modules-----
from src.utils import (
    COLOR_DARK_BLUE,
    COLOR_LIGHT_BLUE,
    THEME_BORDER,
    THEME_TEXT_PRIMARY,
)


def qss() -> str:
    return f"""
    /* === Radio Button === */
    QRadioButton {{
        color: {THEME_TEXT_PRIMARY};
        spacing: 8px;
    }}

    QRadioButton::indicator {{
        width: 18px;
        height: 18px;
        border: 2px solid {THEME_BORDER};
        border-radius: 9px;
        background-color: rgba(255, 255, 255, 0.04);
    }}

    QRadioButton::indicator:hover {{
        border: 2px solid rgba(122, 162, 247, 0.5);
        background-color: rgba(255, 255, 255, 0.06);
    }}

    QRadioButton::indicator:checked {{
        background-color: {COLOR_DARK_BLUE};
        border: 2px solid {COLOR_DARK_BLUE};
    }}

    QRadioButton::indicator:checked:hover {{
        background-color: {COLOR_LIGHT_BLUE};
        border: 2px solid {COLOR_LIGHT_BLUE};
    }}
    """
