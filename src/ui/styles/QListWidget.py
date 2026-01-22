# ----- Utils Modules-----
from src.utils import THEME_BG_SECONDARY, THEME_TEXT_PRIMARY


def qss() -> str:
    return f"""
    /* === List Widget === */
    QListWidget {{
        background-color: {THEME_BG_SECONDARY};
        border-radius: 0px;
        outline: 0;
    }}

    QListWidget::item {{
        background-color: #2D2D2D;
        color: {THEME_TEXT_PRIMARY};
        padding: 0px;
    }}

    QListWidget::item:alternate {{
        background-color: {THEME_BG_SECONDARY};
    }}

    QListWidget::item:hover {{
        background-color: #444444;
    }}

    QListWidget::item:selected {{
        background-color: #3B5689;
    }}

    QListWidget::item:selected:hover {{
        background-color: #546C98;
    }}

    QListWidget::item:focus {{
        background-color: #444444;
    }}
    """
