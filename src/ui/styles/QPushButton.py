# ----- Utils Modules-----
from src.utils import (
    COLOR_DARK_BLUE,
    COLOR_LIGHT_BLUE,
    COLOR_ORANGE,
    THEME_BORDER,
    THEME_TEXT_PRIMARY,
    AccentTheme,
)


def qss() -> str:
    # Get the app's accent color theme
    accent: dict[str, str] = AccentTheme.get()

    return f"""
    /* === Buttons === */
    QPushButton {{
        background-color: rgba(255, 255, 255, 0.04);
        color: {THEME_TEXT_PRIMARY};
        border-radius: 0px;
        padding: 3px 10px;
        height: 18px;
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

    /* === About Close Button === */
    #AboutCloseButton {{
        background-color: {accent['main_background']};
        color: {THEME_TEXT_PRIMARY};
        border: none;
        border-radius: 4px;
        padding: 10px 24px;
        font-size: 10pt;
        font-weight: bold;
    }}
    #AboutCloseButton:hover {{
        background-color: {accent['hover_background']};
    }}
    #AboutCloseButton:pressed {{
        background-color: {accent['pressed_background']};
    }}

    /* === Browse Button === */
    QPushButton[BrowseButton="true"] {{
        background-color: rgba(255, 255, 255, 0.04);
        color: {THEME_TEXT_PRIMARY};
        border-radius: 4px;
        padding: 4px 12px;
    }}
    QPushButton[BrowseButton="true"]:hover {{
        background-color: {accent['hover_background']};
        border-bottom: 2px solid {accent['border']};
    }}
    QPushButton[BrowseButton="true"]:pressed {{
        background-color: {accent['pressed_background']};
    }}
    QPushButton[BrowseButton="true"]:focus {{
        background-color: {accent['hover_background']};
        border-bottom: 2px solid {accent['border']};
        outline: none;
    }}

    /* === Validate Button === */
    QPushButton[ValidateButton="true"] {{
        background-color: rgba(255, 158, 100, 0.08);
        color: {COLOR_ORANGE};
        border-radius: 4px;
        padding: 4px 12px;
    }}
    QPushButton[ValidateButton="true"]:hover {{
        background-color: rgba(255, 158, 100, 0.12);
        border-bottom: 2px solid {COLOR_ORANGE};
    }}
    QPushButton[ValidateButton="true"]:pressed {{
        background-color: rgba(255, 158, 100, 0.16);
    }}
    QPushButton[ValidateButton="true"]:focus {{
        background-color: rgba(255, 158, 100, 0.12);
        border-bottom: 2px solid {COLOR_ORANGE};
        outline: none;
    }}

    /* === Save Button === */
    QPushButton[SaveButton="true"] {{
        background-color: rgba(158, 206, 106, 0.2);
        color: #9ece6a;
        border-radius: 4px;
        padding: 6px 16px;
    }}
    QPushButton[SaveButton="true"]:hover {{
        background-color: rgba(158, 206, 106, 0.3);
        border-bottom: 2px solid #9ece6a;
    }}
    QPushButton[SaveButton="true"]:pressed {{
        background-color: rgba(158, 206, 106, 0.4);
    }}
    QPushButton[SaveButton="true"]:focus {{
        background-color: rgba(158, 206, 106, 0.3);
        border-bottom: 2px solid #9ece6a;
        outline: none;
    }}

    /* === Cancel Button === */
    QPushButton[CancelButton="true"] {{
        background-color: rgba(255, 255, 255, 0.04);
        color: {THEME_TEXT_PRIMARY};
        border-radius: 4px;
        padding: 6px 16px;
    }}
    QPushButton[CancelButton="true"]:hover {{
        background-color: {accent['hover_background']};
        border-bottom: 2px solid {accent['border']};
    }}
    QPushButton[CancelButton="true"]:pressed {{
        background-color: {accent['pressed_background']};
    }}
    QPushButton[CancelButton="true"]:focus {{
        background-color: {accent['hover_background']};
        border-bottom: 2px solid {accent['border']};
        outline: none;
    }}

    /* === Remove Button === */
    QPushButton[RemoveButton="true"] {{
        background-color: rgba(247, 118, 142, 0.2);
        color: #f7768e;
        border-radius: 4px;
        padding: 6px 16px;
    }}
    QPushButton[RemoveButton="true"]:hover {{
        background-color: rgba(247, 118, 142, 0.3);
        border-bottom: 2px solid #f7768e;
    }}
    QPushButton[RemoveButton="true"]:pressed {{
        background-color: rgba(247, 118, 142, 0.4);
    }}
    QPushButton[RemoveButton="true"]:focus {{
        background-color: rgba(247, 118, 142, 0.3);
        border-bottom: 2px solid #f7768e;
        outline: none;
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

    /* === Collapse Button === */
    QPushButton[CollapseButton="true"] {{
        background-color: transparent;
        border: none;
        border-radius: 4px;
        padding: 2px;
    }}
    QPushButton[CollapseButton="true"]:hover {{
        background-color: {accent['hover_background']};
    }}
    QPushButton[CollapseButton="true"]:pressed {{
        background-color: {accent['pressed_background']};
    }}
    """
