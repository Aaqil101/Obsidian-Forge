# ----- Utils Modules-----
from src.utils import THEME_TEXT_PRIMARY


def qss() -> str:
    return f"""
    /* === Check Box === */
    QCheckBox {{
        color: {THEME_TEXT_PRIMARY};
        spacing: 8px;
    }}

    QCheckBox::indicator {{
        width: 0px;
        height: 0px;
        border: none;
        background: transparent;
    }}
    """
