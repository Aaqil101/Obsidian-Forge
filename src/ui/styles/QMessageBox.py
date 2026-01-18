# ----- Utils Modules-----
from src.utils import THEME_BG_SECONDARY, THEME_TEXT_PRIMARY


def qss() -> str:
    return f"""
    /* ===  Message Box === */
    QMessageBox {{
        background-color: {THEME_BG_SECONDARY};
    }}

    QMessageBox QLabel {{
        color: {THEME_TEXT_PRIMARY};
    }}

    QMessageBox QPushButton {{
        min-width: 80px;
        padding: 8px 20px;
    }}
    """
