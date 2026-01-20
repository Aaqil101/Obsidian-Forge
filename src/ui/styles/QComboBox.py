# ----- Utils Modules -----
from src.utils import COLOR_DARK_BLUE, THEME_BG_PRIMARY, THEME_TEXT_PRIMARY


def qss() -> str:
    return f"""
    QComboBox {{
        background-color: rgba(255, 255, 255, 0.04);
        color: {THEME_TEXT_PRIMARY};
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 3px;
        padding: 1px 1px 1px 3px;
    }}
    QComboBox:hover {{
        background-color: rgba(255, 255, 255, 0.06);
        border-bottom: 2px solid {COLOR_DARK_BLUE};
    }}
    QComboBox:focus {{
        background-color: rgba(255, 255, 255, 0.06);
        border-bottom: 2px solid {COLOR_DARK_BLUE};
        outline: none;
    }}
    QComboBox::drop-down {{
        subcontrol-origin: padding;
        subcontrol-position: top right;
        width: 20px;
        border: none;
        background: transparent;
    }}
    QComboBox::down-arrow {{
        image: url(:/assets/expand_more.svg);
        width: 10px;
        height: 10px;
        border: none;
    }}
    QComboBox::down-arrow:on {{
        image: url(:/assets/expand_less.svg);
    }}

    /* Dropdown list styling */
    QComboBox QAbstractItemView {{
        background-color: {THEME_BG_PRIMARY};
        color: {THEME_TEXT_PRIMARY};
        border-radius: 4px;
        selection-background-color: {COLOR_DARK_BLUE};
        selection-color: {THEME_TEXT_PRIMARY};
        show-decoration-selected: 1;
        outline: none;
    }}
    QComboBox QAbstractItemView::item {{
        background-color: {THEME_BG_PRIMARY};
        color: {THEME_TEXT_PRIMARY};
        height: 20px;
        padding: 2px 4px;
        border: none;
    }}
    QComboBox QAbstractItemView::item:hover {{
        background-color: rgba(83, 144, 247, 0.25);
        color: {THEME_TEXT_PRIMARY};
    }}
    QComboBox QAbstractItemView::item:selected {{
        background-color: rgba(83, 144, 247, 0.25);
        color: {THEME_TEXT_PRIMARY};
    }}
    QComboBox QAbstractItemView::item:selected:hover {{
        background-color: rgba(83, 144, 247, 0.25);
        border: none;
    }}
    """
