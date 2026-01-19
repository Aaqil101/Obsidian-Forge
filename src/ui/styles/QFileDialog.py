# ----- Core Modules-----
from src.core import BORDER_RADIUS_SMALL

# ----- Utils Modules-----
from src.utils import (
    COLOR_DARK_BLUE,
    COLOR_GREEN,
    COLOR_LIGHT_BLUE,
    THEME_BG_PRIMARY,
    THEME_BG_SECONDARY,
    THEME_BORDER,
    THEME_TEXT_PRIMARY,
    THEME_TEXT_SECONDARY,
)


def qss() -> str:
    return f"""
    /* === Main Dialog === */
    QFileDialog {{
        background-color: {THEME_BG_PRIMARY};
        color: {THEME_TEXT_PRIMARY};
    }}

    /* === Tree View === */
    QTreeView {{
        background-color: #282828;
        color: #E6E6E6;
        border: 1px solid #444444;
        outline: 0;
    }}

    QTreeView::item:hover {{
        background-color: #4F4F4F;
    }}

    QTreeView::item:selected {{
        background-color: #3B5689;
    }}

    QTreeView::item:selected:!active {{
        color: #E6E6E6;
    }}

    /* === List View === */
    QListView {{
        background-color: #282828;
        color: #E6E6E6;
        border: 1px solid #444444;
        outline: 0;
    }}

    QListView::item:hover {{
        background-color: #4F4F4F;
    }}

    QListView::item:selected {{
        background-color: #3B5689;
    }}

    QListView::item:selected:!active {{
        color: #E6E6E6;
    }}

    /* === Header View === */
    QHeaderView {{
        background-color: #282828;
        color: #E6E6E6;
    }}

    QHeaderView::section {{
        background-color: rgba(255, 255, 255, 0.04);
        border: 0.5px solid rgba(255, 255, 255, 0.08);
    }}

    /* === ComboBox === */
    QComboBox {{
        background-color: rgba(255, 255, 255, 0.04);
        color: {THEME_TEXT_PRIMARY};
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 3px;
        padding: 2px 8px 2px 8px;
        padding-right: 24px;
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
        min-height: 24px;
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

    /* === Labels === */
    QLabel {{
        background-color: transparent;
        color: "#FFFFFF";
    }}

    /* === Line Edit === */
    QLineEdit {{
        background-color: rgba(255, 255, 255, 0.04);
        color: {THEME_TEXT_PRIMARY};
        border-radius: 4px;
        padding: 2px;
        border: 2px solid transparent;
    }}
    QLineEdit:focus {{
        background-color: #222;
        border-bottom: 2px solid {COLOR_DARK_BLUE};
        border-right: 2px solid {COLOR_DARK_BLUE};
        font-style: unset;
    }}

    /* === Buttons === */
    QPushButton {{
        background-color: rgba(255, 255, 255, 0.04);
        color: {THEME_TEXT_PRIMARY};
        border-radius: 4px;
        padding: 4px 12px;
    }}
    QPushButton:hover {{
        background-color: rgba(255, 255, 255, 0.08);
        border-bottom: 2px solid {COLOR_DARK_BLUE};
    }}
    QPushButton:pressed {{
        background-color: rgba(255, 255, 255, 0.12);
    }}
    QPushButton:focus {{
        background-color: rgba(255, 255, 255, 0.08);
        border-bottom: 2px solid {COLOR_DARK_BLUE};
        outline: none;
    }}

    /* === Tool Button === */
    QToolButton {{
        background-color: rgba(255, 255, 255, 0.04);
        border: none;
        border-radius: {BORDER_RADIUS_SMALL}px;
        padding: 4px;
    }}
    QToolButton:hover {{
        background-color: rgba(122, 162, 247, 0.15);
    }}
    QToolButton:pressed {{
        background-color: rgba(122, 162, 247, 0.25);
    }}
    """
