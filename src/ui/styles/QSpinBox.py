# ----- Core Modules-----
from src.core import BORDER_RADIUS_SMALL

# ----- Utils Modules-----
from src.utils import COLOR_DARK_BLUE, THEME_BORDER, THEME_TEXT_PRIMARY


def qss() -> str:
    return f"""
    /* === Spin Box === */
    QSpinBox, QDoubleSpinBox {{
        background-color: rgba(255, 255, 255, 0.04);
        color: {THEME_TEXT_PRIMARY};
        border: 1px solid {THEME_BORDER};
        border-radius: {BORDER_RADIUS_SMALL}px;
        padding: 6px 10px;
    }}

    QSpinBox:hover, QDoubleSpinBox:hover {{
        background-color: rgba(255, 255, 255, 0.06);
        border: 1px solid rgba(122, 162, 247, 0.5);
    }}

    QSpinBox:focus, QDoubleSpinBox:focus {{
        background-color: #222;
        border: 1px solid {COLOR_DARK_BLUE};
    }}

    QSpinBox::up-button, QDoubleSpinBox::up-button {{
        background-color: transparent;
        border: none;
        border-left: 1px solid {THEME_BORDER};
        border-radius: 0;
        width: 20px;
    }}

    QSpinBox::up-button:hover, QDoubleSpinBox::up-button:hover {{
        background-color: rgba(122, 162, 247, 0.15);
    }}

    QSpinBox::down-button, QDoubleSpinBox::down-button {{
        background-color: transparent;
        border: none;
        border-left: 1px solid {THEME_BORDER};
        border-radius: 0;
        width: 20px;
    }}

    QSpinBox::down-button:hover, QDoubleSpinBox::down-button:hover {{
        background-color: rgba(122, 162, 247, 0.15);
    }}
    """
