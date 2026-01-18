"""
Script card widget - entire card is clickable to execute scripts.
Inspired by Blender-Launcher-V2 design.
"""

# ----- PySide6 Modules -----
from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

# ----- Core Modules -----
from src.core import (
    ANIMATION_DURATION,
    APP_NAME,
    APP_VERSION,
    AUTHOR,
    BORDER_RADIUS,
    BORDER_RADIUS_LARGE,
    BORDER_RADIUS_SMALL,
    DAILY_SCRIPTS_PATH,
    FONT_FAMILY,
    FONT_SIZE_HEADER,
    FONT_SIZE_LABEL,
    FONT_SIZE_SMALL,
    FONT_SIZE_TEXT,
    FONT_SIZE_TITLE,
    HOVER_DURATION,
    PADDING,
    PADDING_LARGE,
    PADDING_SMALL,
    SPACING,
    SPACING_LARGE,
    SPACING_SMALL,
    TIME_PATH,
    UTILS_SCRIPTS_PATH,
    WEEKLY_SCRIPTS_PATH,
    WINDOW_MIN_HEIGHT,
    WINDOW_MIN_WIDTH,
)

# ----- Utils Modules -----
from src.utils import THEME_BG_SECONDARY, THEME_BORDER, THEME_TEXT_PRIMARY, get_icon


class ScriptRow(QFrame):
    """
    A clickable card widget for executing scripts.
    The entire card acts as a button with proper elevation.

    Signals:
        execute_clicked: Emitted when the card is clicked
    """

    execute_clicked = Signal()

    def __init__(
        self,
        name: str,
        icon_name: str = "file.svg",
        description: str = "",
        script_type: str = "",
        parent: QWidget | None = None,
    ) -> None:
        """
        Create a script row widget.

        Args:
            name: Script display name
            icon_name: Icon filename (e.g., 'daily.svg')
            description: Tooltip description
            script_type: Type of script (e.g., 'daily', 'weekly')
            parent: Parent widget (optional)
        """
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(55)
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setStyleSheet(
            f"""
            /* === Script Row (Button-like Card) === */
            QFrame {{
                background-color: rgba(83, 144, 247, 0.2);
                color: white;
                border-radius: {BORDER_RADIUS}px;
            }}

            QFrame:hover {{
                background-color: rgba(83, 144, 247, 0.3);
                border-bottom: 2px solid rgb(83, 144, 247);
                border-left: 2px solid rgb(83, 144, 247);
            }}

            QLabel {{
                background: transparent;
                border: none;
            }}

            QToolTip {{
                color: #E6E6E6;
                font: 10pt "Open Sans SemiBold";
                background-color: #19191A;
                border: 1px solid #323232;
            }}
            """
        )
        self.name: str = name
        self._pressed = False

        # Main vertical layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 6, 10, 6)
        main_layout.setSpacing(2)

        # Icon and name row
        name_row = QHBoxLayout()
        name_row.setSpacing(8)

        # Icon
        icon_label = QLabel()
        icon_label.setPixmap(get_icon(icon_name).pixmap(QSize(16, 16)))
        icon_label.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        icon_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        name_row.addWidget(icon_label)

        # Title label
        self.title_label = QLabel(name, self)
        self.title_label.setProperty("CardTitle", True)
        self.title_label.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.title_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        name_row.addWidget(self.title_label)
        name_row.addStretch()

        main_layout.addLayout(name_row)

        # Script type subtitle
        self.subtitle_label = QLabel(
            script_type.capitalize() if script_type else "", self
        )
        self.subtitle_label.setProperty("CardSubtitle", True)
        self.subtitle_label.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.subtitle_label.setAttribute(
            Qt.WidgetAttribute.WA_TransparentForMouseEvents
        )
        main_layout.addWidget(self.subtitle_label)

        # Set tooltip
        tooltip: str = f"Click to execute {name}"
        if description:
            tooltip = f"{description}\nClick to execute"
        self.setToolTip(tooltip)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """Handle mouse press - add pressed visual state."""
        if event.button() == Qt.MouseButton.LeftButton:
            self._pressed = True
            self.setStyleSheet(
                f"""
                QFrame {{
                    background-color: rgba(83, 144, 247, 0.3);
                    border-bottom: 2px solid rgb(83, 144, 247);
                    border-left: 2px solid rgb(83, 144, 247);
                    border-radius: {BORDER_RADIUS}px;
                }}
                QLabel {{
                    background: transparent;
                    border: none;
                }}
                """
            )
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        """Handle mouse release - emit signal and restore style."""
        if event.button() == Qt.MouseButton.LeftButton and self._pressed:
            self._pressed = False
            # Restore normal style
            self.setStyleSheet(
                f"""
                QFrame {{
                    background-color: rgba(83, 144, 247, 0.2);
                    color: white;
                    border-radius: {BORDER_RADIUS}px;
                }}

                QFrame:hover {{
                    background-color: rgba(83, 144, 247, 0.3);
                    border-bottom: 2px solid rgb(83, 144, 247);
                    border-left: 2px solid rgb(83, 144, 247);
                }}
                QLabel {{
                    background: transparent;
                    border: none;
                }}
                """
            )
            # Emit signal if released inside the widget
            if self.rect().contains(event.pos()):
                self.execute_clicked.emit()
        super().mouseReleaseEvent(event)

    def setEnabled(self, enabled: bool) -> None:
        """Enable or disable the card."""
        super().setEnabled(enabled)
        self.title_label.setEnabled(enabled)
        self.setCursor(
            Qt.CursorShape.PointingHandCursor
            if enabled
            else Qt.CursorShape.ForbiddenCursor
        )
