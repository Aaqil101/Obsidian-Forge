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
    Enhanced with Blender-Launcher-V2 component styling patterns.

    Returns:
        Complete stylesheet string for QApplication
    """
    return f"""
        /* === Main Window === */
        QMainWindow {{
            background-color: {THEME_BG_PRIMARY};
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
            color: {COLOR_LIGHT_BLUE};
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

        QMenu::icon {{
            padding-left: 8px;
        }}

        QMenu::item {{
            padding: 6px 24px 6px 10px;
            border-radius: {BORDER_RADIUS_SMALL}px;
        }}

        QMenu::item:selected {{
            background-color: rgba(122, 162, 247, 0.2);
            color: #FFFFFF;
        }}

        QMenu::item:disabled {{
            color: {THEME_TEXT_SUBTLE};
        }}

        QMenu::separator {{
            height: 1px;
            background-color: {THEME_BORDER};
            margin: 4px 8px;
        }}

        /* === Custom Menu Items === */
        #MenuItem {{
            background-color: transparent;
            border-radius: {BORDER_RADIUS_SMALL}px;
            min-width: 120px;
        }}

        #MenuItem:hover {{
            background-color: rgba(122, 162, 247, 0.15);
        }}

        #MenuItemText {{
            background-color: transparent;
            color: {THEME_TEXT_PRIMARY};
        }}

        #MenuItemShortcut {{
            background-color: transparent;
            color: {THEME_TEXT_SUBTLE};
            font-size: {FONT_SIZE_SMALL}pt;
        }}

        /* === Labels === */
        QLabel {{
            color: {THEME_TEXT_PRIMARY};
            background-color: transparent;
        }}

        /* === Tab Widget === */
        QTabWidget::pane {{
            background-color: {THEME_BG_PRIMARY};
            border: 1px solid {THEME_BORDER};
            border-radius: {BORDER_RADIUS_SMALL}px;
        }}
        QTabBar::tab {{
            background-color: {THEME_BG_SECONDARY};
            color: {THEME_TEXT_SECONDARY};
            padding: 8px 16px;
            margin-right: 2px;
            border-top-left-radius: {BORDER_RADIUS_SMALL}px;
            border-top-right-radius: {BORDER_RADIUS_SMALL}px;
        }}
        QTabBar::tab:hover {{
            background-color: rgba(122, 162, 247, 0.1);
            color: {THEME_TEXT_PRIMARY};
        }}
        QTabBar::tab:selected {{
            background-color: rgba(122, 162, 247, 0.2);
            color: #FFFFFF;
            font-weight: bold;
        }}
        QTabBar::tab:disabled {{
            color: {THEME_TEXT_SUBTLE};
        }}
        QTabBar:focus {{
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
            background-color: {THEME_BG_PRIMARY};
            color: {THEME_TEXT_PRIMARY};
        }}

        QDialog QFrame {{
            background-color: transparent;
        }}

        /* === Message Box === */
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

        /* === Search Bar === */
        QLineEdit[SearchBar="true"] {{
            background-color: rgba(255, 255, 255, 0.04);
            color: {THEME_TEXT_PRIMARY};
            border: 1px solid {THEME_BORDER};
            border-radius: {BORDER_RADIUS_SMALL}px;
            padding: 6px 8px 6px 0px;
            font-size: {FONT_SIZE_SMALL}pt;
        }}

        QLineEdit[SearchBar="true"]:focus {{
            background-color: rgba(255, 255, 255, 0.06);
            border: 1px solid {COLOR_DARK_BLUE};
        }}

        /* === Script Card === */
        QFrame[ScriptCard="true"] {{
            background-color: rgba(255, 255, 255, 0.03);
            border: 1px solid {THEME_BORDER};
            border-radius: {BORDER_RADIUS_SMALL}px;
        }}

        QFrame[ScriptCard="true"]:hover {{
            background-color: rgba(122, 162, 247, 0.1);
            border: 1px solid {COLOR_DARK_BLUE};
        }}

        /* === Script Row (Button Cards) === */
        QWidget[ScriptRow="true"] {{
            background-color: rgba(25, 30, 40, 0.6);
            border: 1px solid rgba(50, 60, 75, 0.6);
            border-radius: {BORDER_RADIUS_SMALL}px;
        }}

        QWidget[ScriptRow="true"]:hover {{
            background-color: rgba(35, 42, 55, 0.8);
            border: 1px solid rgba(80, 95, 115, 0.8);
        }}

        QWidget[ScriptRow="true"]:disabled {{
            background-color: rgba(20, 25, 35, 0.4);
            border: 1px solid rgba(40, 45, 55, 0.5);
            opacity: 0.5;
        }}

        QWidget[ScriptRow="true"] QLabel {{
            background: transparent;
            color: {THEME_TEXT_PRIMARY};
        }}

        /* === Card Title === */
        QLabel[CardTitle="true"] {{
            color: {THEME_TEXT_PRIMARY};
            font-size: {FONT_SIZE_SMALL + 1}pt;
            font-weight: bold;
            background-color: transparent;
        }}

        /* === Card Subtitle === */
        QLabel[CardSubtitle="true"] {{
            color: {THEME_TEXT_SUBTLE};
            font-size: {FONT_SIZE_SMALL}pt;
            background-color: transparent;
        }}

        /* === Primary Button === */
        QPushButton[PrimaryButton="true"] {{
            background-color: {COLOR_DARK_BLUE};
            color: #FFFFFF;
            border: 1px solid {COLOR_DARK_BLUE};
        }}

        QPushButton[PrimaryButton="true"]:hover {{
            background-color: {COLOR_LIGHT_BLUE};
            border: 1px solid {COLOR_LIGHT_BLUE};
        }}

        QPushButton[PrimaryButton="true"]:pressed {{
            background-color: #4a6cb8;
        }}

        /* === Secondary Button === */
        QPushButton[SecondaryButton="true"] {{
            background-color: rgba(255, 255, 255, 0.06);
            color: {THEME_TEXT_PRIMARY};
            border: 1px solid {THEME_BORDER};
        }}

        QPushButton[SecondaryButton="true"]:hover {{
            background-color: rgba(255, 255, 255, 0.1);
            color: #FFFFFF;
            border: 1px solid rgba(122, 162, 247, 0.5);
        }}

        QPushButton[SecondaryButton="true"]:pressed {{
            background-color: rgba(255, 255, 255, 0.08);
        }}

        /* === Danger/Cancel Button === */
        QPushButton[CancelButton="true"] {{
            background-color: rgba(247, 118, 142, 0.15);
            color: #f7768e;
            border: 1px solid rgba(247, 118, 142, 0.3);
        }}

        QPushButton[CancelButton="true"]:hover {{
            background-color: rgba(247, 118, 142, 0.25);
            color: #FFFFFF;
            border: 1px solid #f7768e;
        }}

        QPushButton[CancelButton="true"]:pressed {{
            background-color: rgba(247, 118, 142, 0.35);
        }}

        /* === Popup Button === */
        QPushButton[Popup="true"] {{
            background-color: rgba(255, 255, 255, 0.08);
            color: {THEME_TEXT_PRIMARY};
            border: 1px solid {THEME_BORDER};
            padding: 8px 20px;
            min-width: 80px;
        }}

        QPushButton[Popup="true"]:hover {{
            background-color: rgba(122, 162, 247, 0.2);
            color: #FFFFFF;
            border: 1px solid {COLOR_LIGHT_BLUE};
        }}

        /* === Tool Button === */
        QToolButton {{
            background-color: transparent;
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

        /* === Combo Box === */
        QComboBox {{
            background-color: rgba(255, 255, 255, 0.04);
            color: {THEME_TEXT_PRIMARY};
            border: 1px solid {THEME_BORDER};
            border-radius: {BORDER_RADIUS_SMALL}px;
            padding: 6px 10px;
            min-width: 100px;
        }}

        QComboBox:hover {{
            background-color: rgba(255, 255, 255, 0.06);
            border: 1px solid rgba(122, 162, 247, 0.5);
        }}

        QComboBox:focus {{
            background-color: #222;
            border: 1px solid {COLOR_DARK_BLUE};
        }}

        QComboBox::drop-down {{
            border: none;
            padding-right: 8px;
        }}

        QComboBox::down-arrow {{
            image: none;
            border-left: 4px solid transparent;
            border-right: 4px solid transparent;
            border-top: 5px solid {THEME_TEXT_PRIMARY};
            margin-right: 5px;
        }}

        QComboBox QAbstractItemView {{
            background-color: {THEME_BG_SECONDARY};
            color: {THEME_TEXT_PRIMARY};
            border: 1px solid {THEME_BORDER};
            border-radius: {BORDER_RADIUS_SMALL}px;
            selection-background-color: rgba(122, 162, 247, 0.3);
            selection-color: #FFFFFF;
            padding: 4px;
        }}

        QComboBox QAbstractItemView::item {{
            padding: 6px 10px;
            border-radius: {BORDER_RADIUS_SMALL - 2}px;
        }}

        QComboBox QAbstractItemView::item:hover {{
            background-color: rgba(122, 162, 247, 0.15);
        }}

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

        /* === Check Box === */
        QCheckBox {{
            color: {THEME_TEXT_PRIMARY};
            spacing: 8px;
        }}

        QCheckBox::indicator {{
            width: 18px;
            height: 18px;
            border: 2px solid {THEME_BORDER};
            border-radius: {BORDER_RADIUS_SMALL - 2}px;
            background-color: rgba(255, 255, 255, 0.04);
        }}

        QCheckBox::indicator:hover {{
            border: 2px solid rgba(122, 162, 247, 0.5);
            background-color: rgba(255, 255, 255, 0.06);
        }}

        QCheckBox::indicator:checked {{
            background-color: {COLOR_DARK_BLUE};
            border: 2px solid {COLOR_DARK_BLUE};
        }}

        QCheckBox::indicator:checked:hover {{
            background-color: {COLOR_LIGHT_BLUE};
            border: 2px solid {COLOR_LIGHT_BLUE};
        }}

        QCheckBox::indicator:disabled {{
            background-color: rgba(255, 255, 255, 0.02);
            border: 2px solid rgba(255, 255, 255, 0.1);
        }}

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

        /* === Progress Bar === */
        QProgressBar {{
            background-color: rgba(255, 255, 255, 0.04);
            border: 1px solid {THEME_BORDER};
            border-radius: {BORDER_RADIUS_SMALL}px;
            text-align: center;
            color: {THEME_TEXT_PRIMARY};
            height: 20px;
        }}

        QProgressBar::chunk {{
            background-color: {COLOR_DARK_BLUE};
            border-radius: {BORDER_RADIUS_SMALL - 1}px;
        }}

        /* === Slider === */
        QSlider::groove:horizontal {{
            background-color: rgba(255, 255, 255, 0.04);
            border: 1px solid {THEME_BORDER};
            height: 6px;
            border-radius: 3px;
        }}

        QSlider::handle:horizontal {{
            background-color: {COLOR_LIGHT_BLUE};
            border: 2px solid {COLOR_DARK_BLUE};
            width: 16px;
            margin: -6px 0;
            border-radius: 8px;
        }}

        QSlider::handle:horizontal:hover {{
            background-color: #FFFFFF;
            border: 2px solid {COLOR_LIGHT_BLUE};
        }}
        """
