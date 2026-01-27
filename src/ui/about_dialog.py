"""
About dialog for Obsidian Forge.
A visually appealing dialog with Tokyo Night theme styling.
"""

# ----- PySide6 Modules-----
from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QColor, QLinearGradient, QPainter, QPen
from PySide6.QtWidgets import (
    QDialog,
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)

# ----- Core Modules-----
from src.core import APP_NAME, APP_VERSION, AUTHOR, DESCRIPTION, WEBSITE_URL

# ----- Utils Modules-----
from src.utils import (
    COLOR_CYAN,
    COLOR_LIGHT_BLUE,
    COLOR_PURPLE,
    COLOR_RED,
    THEME_TEXT_PRIMARY,
    HoverIconButtonSVG,
    get_icon,
)


class GlowingLine(QFrame):
    """A horizontal line with a glowing gradient effect."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setFixedHeight(2)
        self.setStyleSheet("background: transparent;")

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        gradient = QLinearGradient(0, 0, self.width(), 0)
        gradient.setColorAt(0.0, QColor(COLOR_PURPLE))
        gradient.setColorAt(0.5, QColor(COLOR_LIGHT_BLUE))
        gradient.setColorAt(1.0, QColor(COLOR_CYAN))

        pen = QPen()
        pen.setBrush(gradient)
        pen.setWidth(2)
        painter.setPen(pen)
        painter.drawLine(0, 1, self.width(), 1)


class FeatureItem(QWidget):
    """A single feature item with icon and text."""

    def __init__(self, icon_name: str, text: str, parent=None) -> None:
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 4, 0, 4)
        layout.setSpacing(8)

        layout.addStretch()  # Add stretch before to center content

        icon_label = QLabel()
        icon_label.setPixmap(get_icon(icon_name).pixmap(QSize(16, 16)))
        icon_label.setStyleSheet("background: transparent;")
        layout.addWidget(icon_label)

        text_label = QLabel(text)
        text_label.setObjectName("FeatureTextLabel")

        layout.addWidget(text_label)
        layout.addStretch()  # Add stretch after to center content


class AboutDialog(QDialog):
    """A stylish about dialog for Obsidian Forge."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle(f"About {APP_NAME}")
        self.setFixedSize(350, 450)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.setup_ui()
        self.center_on_parent()

    def setup_ui(self) -> None:
        """Setup the dialog UI."""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Container with rounded corners and shadow
        container = QFrame()
        container.setObjectName("AboutContainer")

        # Add drop shadow
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setXOffset(0)
        shadow.setYOffset(4)
        shadow.setColor(QColor(0, 0, 0, 100))
        container.setGraphicsEffect(shadow)

        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(12, 12, 12, 12)
        container_layout.setSpacing(8)

        # Header section with icon and app name
        header_widget = QWidget()
        header_layout = QVBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(12)
        header_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # App icon
        icon_label = QLabel()
        icon_label.setPixmap(
            get_icon("application/obsidian_forge.svg").pixmap(QSize(72, 72))
        )
        icon_label.setStyleSheet("background: transparent;")
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(icon_label)

        # App name with gradient effect
        app_name_label = QLabel(APP_NAME)
        app_name_label.setObjectName("AppNameLabel")
        app_name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        header_layout.addWidget(app_name_label)

        # Version badge
        version_widget = QWidget()
        version_layout = QHBoxLayout(version_widget)
        version_layout.setContentsMargins(0, 0, 0, 0)
        version_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        version_label = QLabel(f"v{APP_VERSION}")
        version_label.setObjectName("VersionLabel")

        version_layout.addWidget(version_label)
        header_layout.addWidget(version_widget)

        container_layout.addWidget(header_widget)

        # Glowing separator
        container_layout.addWidget(GlowingLine())

        # Description
        desc_label = QLabel(DESCRIPTION)
        desc_label.setObjectName("DescriptionLabel")
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc_label.setWordWrap(True)

        container_layout.addWidget(desc_label)

        # Features section
        features_frame = QFrame()
        features_frame.setObjectName("FeaturesFrame")

        features_layout = QVBoxLayout(features_frame)
        features_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        features_layout.setContentsMargins(4, 4, 4, 4)
        features_layout.setSpacing(2)

        features_title = QLabel("Features")
        features_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        features_title.setObjectName("FeaturesTitleLabel")

        features_layout.addWidget(features_title)

        features = [
            ("daily-weekly/daily.svg", "Daily note quick entries"),
            ("daily-weekly/weekly.svg", "Weekly note quick entries"),
            ("application/nodejs.svg", "Native QuickAdd script support"),
        ]

        for icon, text in features:
            features_layout.addWidget(FeatureItem(icon, text))

        container_layout.addWidget(features_frame)

        # Author section
        author_widget = QWidget()
        author_layout = QHBoxLayout(author_widget)
        author_layout.setContentsMargins(0, 0, 0, 0)
        author_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        author_layout.setSpacing(6)

        created_label = QLabel("Created with")
        created_label.setObjectName("CreatedLabel")

        author_layout.addWidget(created_label)

        heart_label = QLabel("\u2665")  # Heart symbol
        heart_label.setObjectName("HeartLabel")

        author_layout.addWidget(heart_label)

        by_label = QLabel(f"by {AUTHOR}")
        by_label.setObjectName("ByLabel")

        author_layout.addWidget(by_label)

        container_layout.addWidget(author_widget)

        # Website section
        website_label = QLabel(
            f'<a href="{WEBSITE_URL}" style="color: {COLOR_LIGHT_BLUE};">{WEBSITE_URL}</a>'
        )
        website_label.setObjectName("WebsiteLabel")
        website_label.setOpenExternalLinks(True)
        website_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        website_label.setCursor(Qt.CursorShape.PointingHandCursor)
        container_layout.addWidget(website_label)

        # Spacer
        container_layout.addStretch()

        # Close button
        close_btn = HoverIconButtonSVG(
            normal_icon="cancel_outline.svg",
            hover_icon="cancel_outline.svg",
            hover_color=f"{THEME_TEXT_PRIMARY}",
            pressed_icon="cancel.svg",
            pressed_color=f"{COLOR_RED}",
            icon_size=14,
            text="&Cancel",
        )
        close_btn.setObjectName("AboutCloseButton")
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.clicked.connect(self.accept)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(close_btn)
        btn_layout.addStretch()
        container_layout.addLayout(btn_layout)

        main_layout.addWidget(container)

    def center_on_parent(self) -> None:
        """Center the dialog on the parent window."""
        if self.parent():
            parent_geometry = self.parent().geometry()
            dialog_geometry = self.geometry()

            # Calculate center position
            x = (
                parent_geometry.x()
                + (parent_geometry.width() - dialog_geometry.width()) // 2
            )
            y = (
                parent_geometry.y()
                + (parent_geometry.height() - dialog_geometry.height()) // 2
            )

            self.move(x, y)

    def keyPressEvent(self, event) -> None:
        """Handle key press events."""
        if event.key() == Qt.Key.Key_Escape:
            self.accept()
        else:
            super().keyPressEvent(event)
