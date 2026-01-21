# ----- Utils Modules-----
from src.utils import THEME_TEXT_PRIMARY


def qss() -> str:
    return f"""
    QToolTip {{
        color: {THEME_TEXT_PRIMARY};
        font: 10pt "Open Sans SemiBold";
        background-color: #19191A;
        border: 1px solid #323232;
    }}
    """
