"""
Tokyo Night theme stylesheets for Obsidian Forge.
Centralized PySide6 stylesheet definitions following GitUI's style system.
"""

# ----- Core Modules-----
from src.core import BORDER_RADIUS, BORDER_RADIUS_SMALL, FONT_SIZE_SMALL

# ----- Utils Modules-----
from src.utils import (
    COLOR_DARK_BLUE,
    COLOR_LIGHT_BLUE,
    THEME_BG_PRIMARY,
    THEME_BG_SECONDARY,
    THEME_BORDER,
    THEME_TEXT_PRIMARY,
    THEME_TEXT_SECONDARY,
    THEME_TEXT_SUBTLE,
)


def get_main_stylesheet() -> str:
    """
    Get the main application stylesheet with Tokyo Night theme.

    Returns:
        Complete stylesheet string for QApplication
    """
    return f"""
        /* === Main Window === */
        QMainWindow {{
            background-color: {THEME_BG_SECONDARY};
            color: {THEME_TEXT_PRIMARY};
        }}

        /* === Central Widget === */
        QWidget {{
            background-color: {THEME_BG_SECONDARY};
            color: {THEME_TEXT_PRIMARY};
        }}

        /* === Menu Bar === */
        QMenuBar {{
            background-color: {THEME_BG_SECONDARY};
            color: {THEME_TEXT_PRIMARY};
            border-bottom: 1px solid {THEME_BORDER};
            padding: 4px;
        }}

        QMenuBar::item {{
            background-color: transparent;
            padding: 6px 12px;
            border-radius: {BORDER_RADIUS_SMALL}px;
        }}

        QMenuBar::item:selected {{
            background-color: {THEME_BG_PRIMARY};
        }}

        QMenuBar::item:pressed {{
            background-color: {THEME_BG_SECONDARY};
        }}

        /* === Menu === */
        QMenu {{
            background-color: {THEME_BG_SECONDARY};
            color: {THEME_TEXT_PRIMARY};
            border: 1px solid {THEME_BORDER};
            border-radius: {BORDER_RADIUS}px;
            padding: 4px;
        }}

        QMenu::item {{
            padding: 8px 24px 8px 12px;
            border-radius: {BORDER_RADIUS_SMALL}px;
        }}

        QMenu::item:selected {{
            background-color: {THEME_BG_PRIMARY};
        }}

        QMenu::separator {{
            height: 1px;
            background-color: {THEME_BORDER};
            margin: 4px 8px;
        }}

        /* === Labels === */
        QLabel {{
            color: {THEME_TEXT_PRIMARY};
            background-color: transparent;
        }}

        /* === Tab Widget === */
        QTabWidget::pane {{
            background-color: {THEME_BG_PRIMARY};
        }}
        QTabBar::tab {{
            background-color: {THEME_BG_SECONDARY};
            color: {THEME_TEXT_SECONDARY};
            padding: 8px 16px;
            margin-right: 2px;
            font-weight: normal;
        }}
        QTabBar::tab:hover {{
            background-color: rgba(122, 162, 247, 0.1);
            color: {THEME_TEXT_PRIMARY};
        }}
        QTabBar::tab:selected {{
            background-color: rgba(122, 162, 247, 0.2);
            color: {THEME_TEXT_PRIMARY};
            font-weight: bold;
        }}
        QTabBar:focus {{
            background-color: rgba(122, 162, 247, 0.1);
            color: {THEME_TEXT_PRIMARY};
            outline: none;
        }}

        /* === Line Edit === */
        QLineEdit {{
            background-color: rgba(255, 255, 255, 0.04);
            color: {THEME_TEXT_PRIMARY};
            border-radius: {BORDER_RADIUS_SMALL - 2}px;
            padding: 6px 10px;
            border: 2px solid transparent;
        }}
        QLineEdit:focus {{
            background-color: #222;
            border-bottom: 2px solid {COLOR_DARK_BLUE};
            border-right: 2px solid {COLOR_DARK_BLUE};
            font-style: unset;
        }}

        /* === Text Edit === */
        QTextEdit {{
            background-color: rgba(255, 255, 255, 0.04);
            color: {THEME_TEXT_PRIMARY};
            border-radius: {BORDER_RADIUS_SMALL - 2}px;
            padding: 8px;
            selection-background-color: {COLOR_LIGHT_BLUE};
        }}

        QTextEdit:focus {{
            background-color: #222;
            border-bottom: 2px solid {COLOR_DARK_BLUE};
            border-right: 2px solid {COLOR_DARK_BLUE};
            font-style: unset;
        }}

        /* === Scroll Area === */
        QScrollArea {{
            border: none;
            background-color: {THEME_BG_PRIMARY};
        }}
        QScrollArea > QWidget > QWidget {{
            background-color: {THEME_BG_PRIMARY};
        }}

        /* Vertical Scrollbar */
        QScrollBar:vertical {{
            background-color: transparent;
            width: 12px;
            margin: 4px 2px 4px 2px;
            border-radius: {BORDER_RADIUS_SMALL}px;
        }}

        /* Scrollbar Handle (Thumb) */
        QScrollBar::handle:vertical {{
            background-color: rgba(122, 162, 247, 0.3);
            border-radius: {BORDER_RADIUS_SMALL}px;
            min-height: 30px;
            margin: 0px 2px;
        }}

        QScrollBar::handle:vertical:hover {{
            background-color: rgba(122, 162, 247, 0.5);
        }}

        QScrollBar::handle:vertical:pressed {{
            background-color: rgba(122, 162, 247, 0.7);
        }}

        /* Remove arrow buttons */
        QScrollBar::add-line:vertical,
        QScrollBar::sub-line:vertical {{
            height: 0px;
            background: none;
            border: none;
        }}

        /* Scrollbar background track */
        QScrollBar::add-page:vertical,
        QScrollBar::sub-page:vertical {{
            background: rgba(255, 255, 255, 0.02);
            border-radius: {BORDER_RADIUS_SMALL}px;
        }}

        /* Horizontal Scrollbar (if needed) */
        QScrollBar:horizontal {{
            background-color: transparent;
            height: 12px;
            margin: 2px 4px 2px 4px;
            border-radius: {BORDER_RADIUS_SMALL}px;
        }}

        QScrollBar::handle:horizontal {{
            background-color: rgba(122, 162, 247, 0.3);
            border-radius: {BORDER_RADIUS_SMALL}px;
            min-width: 30px;
            margin: 2px 0px;
        }}

        QScrollBar::handle:horizontal:hover {{
            background-color: rgba(122, 162, 247, 0.5);
        }}

        QScrollBar::handle:horizontal:pressed {{
            background-color: rgba(122, 162, 247, 0.7);
        }}

        QScrollBar::add-line:horizontal,
        QScrollBar::sub-line:horizontal {{
            width: 0px;
            background: none;
            border: none;
        }}

        QScrollBar::add-page:horizontal,
        QScrollBar::sub-page:horizontal {{
            background: rgba(255, 255, 255, 0.02);
            border-radius: {BORDER_RADIUS_SMALL}px;
        }}

        /* === Group Box === */
        QGroupBox {{
            background-color: {THEME_BG_SECONDARY};
            border: 1px solid {THEME_BORDER};
            border-radius: {BORDER_RADIUS}px;
            margin-top: 12px;
            padding-top: 12px;
            font-weight: bold;
        }}

        QGroupBox::title {{
            color: {THEME_TEXT_PRIMARY};
            subcontrol-origin: margin;
            left: 12px;
            padding: 0 8px;
        }}

        /* === Dialog === */
        QDialog {{
            background-color: {THEME_BG_SECONDARY};
            color: {THEME_TEXT_PRIMARY};
        }}

        /* === Message Box === */
        QMessageBox {{
            background-color: {THEME_BG_SECONDARY};
        }}

        QMessageBox QLabel {{
            color: {THEME_TEXT_PRIMARY};
        }}

        /* === Info Label === */
        QLabel[InfoBox="true"] {{
            background-color: {THEME_BG_SECONDARY};
            border: 1px solid {THEME_BORDER};
            border-left: 3px solid {COLOR_DARK_BLUE};
            border-radius: {BORDER_RADIUS_SMALL}px;
            padding: 12px;
            color: {THEME_TEXT_PRIMARY};
        }}

        QLabel[InfoLabel="true"] {{
            color: {THEME_TEXT_SUBTLE};
            font-size: {FONT_SIZE_SMALL}pt;
        }}

        /* === List Widget === */
        QListWidget {{
            background-color: rgba(255, 255, 255, 0.04);
            color: {THEME_TEXT_PRIMARY};
            border-radius: {BORDER_RADIUS_SMALL - 2}px;
            padding: 4px;
        }}
        QListWidget::item {{
            padding: 6px;
            border-radius: {BORDER_RADIUS_SMALL - 3}px;
        }}
        QListWidget::item:selected {{
            background-color: rgba(122, 162, 247, 0.3);
        }}
        QListWidget::item:hover {{
            color: {THEME_TEXT_PRIMARY};
            background-color: rgba(255, 255, 255, 0.06);
        }}
        QListWidget::item:selected:!active {{
            color: {THEME_TEXT_PRIMARY};
            background: rgba(255, 255, 255, 0.08);
        }}
        QListWidget:focus {{
            color: {THEME_TEXT_PRIMARY};
            background-color: rgba(255, 255, 255, 0.06);
            outline: none;
        }}

        /* === Splitter === */
        QSplitter::handle {{
            background-color: {THEME_BORDER};
            width: 2px;
        }}

        QSplitter::handle:hover {{
            background-color: {COLOR_DARK_BLUE};
        }}

        /* === Status Bar === */
        QStatusBar {{
            background-color: {THEME_BG_SECONDARY};
            color: {THEME_TEXT_SECONDARY};
            border-top: 1px solid {THEME_BORDER};
        }}
    """
