# ----- Core Modules-----
from src.core import FONT_FAMILY

# ----- Utils Modules-----
from src.utils import (
    COLOR_LIGHT_BLUE,
    THEME_BG_PRIMARY,
    THEME_BG_SECONDARY,
    THEME_TEXT_PRIMARY,
    THEME_TEXT_SECONDARY,
    AccentTheme,
)


def qss() -> str:
    # Get the app's accent color theme
    accent: dict[str, str] = AccentTheme.get()

    return f"""
    /* === Labels === */
    QLabel {{
        background-color: transparent;
        color: {THEME_TEXT_PRIMARY};
    }}

    /* === Info Label === */
    QLabel[InfoBox="true"] {{
        background-color: {THEME_BG_SECONDARY};
        color: {THEME_TEXT_PRIMARY};
        border: 1px solid #444444;
        border-radius: 0px;
        padding: 6px;
    }}

    QLabel[InfoBox="true"]:hover {{
        border-bottom: 2px solid {accent['border']};
        border-right: 2px solid {accent['border']};
    }}

    QLabel[InfoLabel="true"] {{
        color: {THEME_BG_SECONDARY};
        font-size: 9pt;
    }}

    /* === Card Title === */
    QLabel[CardTitle="true"] {{
        color: {THEME_TEXT_PRIMARY};
        font-size: 10pt;
        font-weight: bold;
        background-color: transparent;
    }}

    /* === Card Subtitle === */
    QLabel[CardSubtitle="true"] {{
        color: {THEME_BG_SECONDARY};
        font-size: 9pt;
        background-color: transparent;
    }}

    /* === Section Header === */
    QLabel[SectionHeader="true"] {{
        color: {accent['border']};
        font-size: 9pt;
        font-weight: bold;
        padding: 2px 4px 2px 4px;
    }}

    /* === App Name Label === */
    #AppNameLabel {{
        font-family: "{FONT_FAMILY}";
        font-size: 20pt;
        font-weight: bold;
        color: {THEME_TEXT_PRIMARY};
        background: transparent;
    }}

    /* === Version Label === */
    #VersionLabel {{
        background-color: {accent['main_background']};
        color: {THEME_TEXT_PRIMARY};
        font-size: 9pt;
        font-weight: bold;
        padding: 4px 12px;
        border-radius: 10px;
    }}

    /* === Description Label === */
    #DescriptionLabel {{
        color: {THEME_TEXT_SECONDARY};
        font-size: 10pt;
        line-height: 1.5;
        background: transparent;
    }}

    /* === Features Frame === */
    #FeaturesFrame {{
        background-color: {THEME_BG_PRIMARY};
        border-radius: 8px;
        padding: 4px;
    }}

    /* === Features Title Label === */
    #FeaturesTitleLabel {{
        color: {COLOR_LIGHT_BLUE};
        font-size: 10pt;
        font-weight: bold;
        background: transparent;
        margin-bottom: 4px;
    }}

    /* === Created Label === */
    CreatedLabel {{
        color: {THEME_TEXT_SECONDARY};
        font-size: 9pt;
        background: transparent;
    }}

    /* === Heart Label === */
    #HeartLabel {{
        color: #f7768e;
        font-size: 12px;
        background: transparent;
    }}

    /* === By Label === */
    #ByLabel {{
        color: {THEME_TEXT_SECONDARY};
        font-size: 9pt;
        background: transparent;
    }}

    /* === Website Label === */
    #WebsiteLabel {{
        color: {COLOR_LIGHT_BLUE};
        font-size: 9pt;
        text-decoration: none;
        background: transparent;
    }}

    /* === Feature Item Text Label === */
    #FeatureTextLabel {{
        color: {THEME_TEXT_SECONDARY};
        font-size: 10pt;
        background: transparent;
    }}
    """
