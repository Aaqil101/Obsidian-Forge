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
    QPushButton,
    QVBoxLayout,
    QWidget,
)

# ----- Core Modules-----
from src.core import (
    APP_NAME,
    APP_VERSION,
    AUTHOR,
    BORDER_RADIUS,
    BORDER_RADIUS_LARGE,
    FONT_FAMILY,
    FONT_SIZE_SMALL,
    FONT_SIZE_TEXT,
    FONT_SIZE_TITLE,
    PADDING,
    PADDING_LARGE,
    SPACING,
    SPACING_LARGE,
)

# ----- Utils Modules-----
from src.utils import (
    COLOR_CYAN,
    COLOR_LIGHT_BLUE,
    COLOR_PURPLE,
    THEME_BG_PRIMARY,
    THEME_BG_SECONDARY,
    THEME_BORDER,
    THEME_TEXT_PRIMARY,
    THEME_TEXT_SECONDARY,
    THEME_TEXT_SUBTLE,
    Icons,
    get_icon,
)


class GlowingLine(QFrame):
    """A horizontal line with a glowing gradient effect."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(2)
        self.setStyleSheet("background: transparent;")

    def paintEvent(self, event):
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

    def __init__(self, icon_name: str, text: str, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 4, 0, 4)
        layout.setSpacing(SPACING)

        icon_label = QLabel()
        icon_label.setPixmap(get_icon(icon_name).pixmap(QSize(16, 16)))
        icon_label.setStyleSheet("background: transparent;")
        layout.addWidget(icon_label)

        text_label = QLabel(text)
        text_label.setStyleSheet(
            f"""
            color: {THEME_TEXT_SECONDARY};
            font-size: {FONT_SIZE_TEXT}pt;
            background: transparent;
            """
        )
        layout.addWidget(text_label)
        layout.addStretch()


class AboutDialog(QDialog):
    """A stylish about dialog for Obsidian Forge."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"About {APP_NAME}")
        self.setFixedSize(420, 480)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.setup_ui()

    def setup_ui(self):
        """Setup the dialog UI."""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Container with rounded corners and shadow
        container = QFrame()
        container.setObjectName("AboutContainer")
        container.setStyleSheet(
            f"""
            #AboutContainer {{
                background-color: {THEME_BG_SECONDARY};
                border: 1px solid {THEME_BORDER};
                border-radius: {BORDER_RADIUS_LARGE}px;
            }}
            """
        )

        # Add drop shadow
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setXOffset(0)
        shadow.setYOffset(4)
        shadow.setColor(QColor(0, 0, 0, 100))
        container.setGraphicsEffect(shadow)

        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(
            PADDING_LARGE, PADDING_LARGE, PADDING_LARGE, PADDING_LARGE
        )
        container_layout.setSpacing(SPACING_LARGE)

        # Header section with icon and app name
        header_widget = QWidget()
        header_layout = QVBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(SPACING)
        header_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # App icon
        icon_label = QLabel()
        icon_label.setPixmap(get_icon("obsidian_forge.svg").pixmap(QSize(72, 72)))
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setStyleSheet("background: transparent;")
        header_layout.addWidget(icon_label)

        # App name with gradient effect
        app_name_label = QLabel(APP_NAME)
        app_name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        app_name_label.setStyleSheet(
            f"""
            font-family: "{FONT_FAMILY}";
            font-size: {FONT_SIZE_TITLE}pt;
            font-weight: bold;
            color: {THEME_TEXT_PRIMARY};
            background: transparent;
            """
        )
        header_layout.addWidget(app_name_label)

        # Version badge
        version_widget = QWidget()
        version_layout = QHBoxLayout(version_widget)
        version_layout.setContentsMargins(0, 0, 0, 0)
        version_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        version_label = QLabel(f"v{APP_VERSION}")
        version_label.setStyleSheet(
            f"""
            background-color: rgba(122, 162, 247, 0.2);
            color: {COLOR_LIGHT_BLUE};
            font-size: {FONT_SIZE_SMALL}pt;
            font-weight: bold;
            padding: 4px 12px;
            border-radius: 10px;
            """
        )
        version_layout.addWidget(version_label)
        header_layout.addWidget(version_widget)

        container_layout.addWidget(header_widget)

        # Glowing separator
        container_layout.addWidget(GlowingLine())

        # Description
        desc_label = QLabel(
            "A powerful companion for Obsidian that lets you\n"
            "quickly add content to your daily and weekly notes\n"
            "using your existing QuickAdd scripts."
        )
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet(
            f"""
            color: {THEME_TEXT_SECONDARY};
            font-size: {FONT_SIZE_TEXT}pt;
            line-height: 1.5;
            background: transparent;
            """
        )
        container_layout.addWidget(desc_label)

        # Features section
        features_frame = QFrame()
        features_frame.setStyleSheet(
            f"""
            background-color: {THEME_BG_PRIMARY};
            border-radius: {BORDER_RADIUS}px;
            padding: 4px;
            """
        )
        features_layout = QVBoxLayout(features_frame)
        features_layout.setContentsMargins(PADDING, PADDING, PADDING, PADDING)
        features_layout.setSpacing(4)

        features_title = QLabel("Features")
        features_title.setStyleSheet(
            f"""
            color: {COLOR_LIGHT_BLUE};
            font-size: {FONT_SIZE_TEXT}pt;
            font-weight: bold;
            background: transparent;
            margin-bottom: 4px;
            """
        )
        features_layout.addWidget(features_title)

        features = [
            ("daily.svg", "Daily note quick entries"),
            ("weekly.svg", "Weekly note quick entries"),
            ("nodejs.svg", "Native QuickAdd script support"),
            ("theme.svg", "Tokyo Night theme"),
        ]

        for icon, text in features:
            features_layout.addWidget(FeatureItem(icon, text))

        container_layout.addWidget(features_frame)

        # Author section
        author_widget = QWidget()
        author_layout = QHBoxLayout(author_widget)
        author_layout.setContentsMargins(0, 0, 0, 0)
        author_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        author_layout.setSpacing(SPACING)

        created_label = QLabel("Created with")
        created_label.setStyleSheet(
            f"""
            color: {THEME_TEXT_SUBTLE};
            font-size: {FONT_SIZE_SMALL}pt;
            background: transparent;
            """
        )
        author_layout.addWidget(created_label)

        heart_label = QLabel("\u2665")  # Heart symbol
        heart_label.setStyleSheet(
            f"""
            color: #f7768e;
            font-size: 12px;
            background: transparent;
            """
        )
        author_layout.addWidget(heart_label)

        by_label = QLabel(f"by {AUTHOR}")
        by_label.setStyleSheet(
            f"""
            color: {THEME_TEXT_SUBTLE};
            font-size: {FONT_SIZE_SMALL}pt;
            background: transparent;
            """
        )
        author_layout.addWidget(by_label)

        container_layout.addWidget(author_widget)

        # Spacer
        container_layout.addStretch()

        # Close button
        close_btn = QPushButton(f"{Icons.CHECK}  Close")
        close_btn.setObjectName("AboutCloseButton")
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.setStyleSheet(
            f"""
            #AboutCloseButton {{
                background-color: rgba(122, 162, 247, 0.2);
                color: {COLOR_LIGHT_BLUE};
                border: 1px solid {COLOR_LIGHT_BLUE};
                border-radius: {BORDER_RADIUS}px;
                padding: 10px 24px;
                font-size: {FONT_SIZE_TEXT}pt;
                font-weight: bold;
            }}
            #AboutCloseButton:hover {{
                background-color: rgba(122, 162, 247, 0.3);
            }}
            #AboutCloseButton:pressed {{
                background-color: rgba(122, 162, 247, 0.4);
            }}
            """
        )
        close_btn.clicked.connect(self.accept)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(close_btn)
        btn_layout.addStretch()
        container_layout.addLayout(btn_layout)

        main_layout.addWidget(container)

    def mousePressEvent(self, event):
        """Allow dragging the dialog."""
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = (
                event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            )
            event.accept()

    def mouseMoveEvent(self, event):
        """Handle dialog dragging."""
        if event.buttons() == Qt.MouseButton.LeftButton and hasattr(self, "_drag_pos"):
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()

    def keyPressEvent(self, event):
        """Handle key press events."""
        if event.key() == Qt.Key.Key_Escape:
            self.accept()
        else:
            super().keyPressEvent(event)
