"""Script card widget - entire card is clickable to execute scripts."""

# ----- Built-In Modules-----
import random

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
from src.core import BORDER_RADIUS

# ----- Utils Modules -----
from src.utils import get_icon


class ColorDict:
    """Dictionary for theme colors."""

    BLUE: dict[str, str] = {
        "main_background": "rgba(83, 144, 247, 0.2)",
        "hover_background": "rgba(83, 144, 247, 0.3)",
        "border": "rgb(83, 144, 247)",
    }
    BROWN: dict[str, str] = {
        "main_background": "rgba(255, 166, 75, 0.2)",
        "hover_background": "rgba(255, 166, 75, 0.3)",
        "border": "rgb(255, 166, 75)",
    }
    RED: dict[str, str] = {
        "main_background": "rgba(225, 80, 69, 0.2)",
        "hover_background": "rgba(225, 80, 69, 0.3)",
        "border": "rgb(225, 80, 69)",
    }
    PURPLE: dict[str, str] = {
        "main_background": "rgba(153, 116, 248, 0.2)",
        "hover_background": "rgba(153, 116, 248, 0.3)",
        "border": "rgb(153, 116, 248)",
    }
    GREEN: dict[str, str] = {
        "main_background": "rgba(89, 143, 76, 0.2)",
        "hover_background": "rgba(89, 143, 76, 0.3)",
        "border": "rgb(89, 143, 76)",
    }
    GRAY: dict[str, str] = {
        "main_background": "rgba(151, 151, 151, 0.2)",
        "hover_background": "rgba(151, 151, 151, 0.3)",
        "border": "rgb(151, 151, 151)",
    }

    def random_color() -> dict[str, str]:
        """Return a random color theme dictionary."""
        return random.choice(
            [
                ColorDict.BLUE,
                ColorDict.BROWN,
                ColorDict.RED,
                ColorDict.PURPLE,
                ColorDict.GREEN,
                ColorDict.GRAY,
            ]
        )


class ScriptRow(QFrame):
    """
    A clickable card widget for executing scripts.
    The entire card acts as a button with proper elevation.

    Signals:
        execute_clicked: Emitted when the card is clicked
    """

    execute_clicked = Signal()
    _shared_color_theme: dict[str, str] | None = None

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

        self.name: str = name
        self._pressed = False

        # Use shared color theme, initialize it once on first instance
        if ScriptRow._shared_color_theme is None:
            ScriptRow._shared_color_theme = ColorDict.random_color()
        self.color_theme: dict[str, str] = ScriptRow._shared_color_theme

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

        # Apply styles directly to the widget
        self._apply_normal_style()

    def _apply_normal_style(self) -> None:
        """Apply normal (non-pressed) style."""
        self.setStyleSheet(
            f"""
            QFrame {{
                background-color: {self.color_theme['main_background']};
                color: white;
            }}
            QFrame:hover {{
                background-color: {self.color_theme['hover_background']};
                border-bottom: 2px solid {self.color_theme['border']};
                border-left: 2px solid {self.color_theme['border']};
            }}

            QLabel {{
                background: transparent;
                border: none;
            }}
            """
        )

    def _apply_pressed_style(self) -> None:
        """Apply pressed style."""
        self.setStyleSheet(
            f"""
            QFrame {{
                background-color: {self.color_theme['hover_background']};
                border-bottom: 2px solid {self.color_theme['border']};
                border-left: 2px solid {self.color_theme['border']};
            }}

            QLabel {{
                background: transparent;
                border: none;
            }}
            """
        )

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """Handle mouse press - add pressed visual state."""
        if event.button() == Qt.MouseButton.LeftButton:
            self._pressed = True
            self._apply_pressed_style()

        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        """Handle mouse release - emit signal and restore style."""
        if event.button() == Qt.MouseButton.LeftButton and self._pressed:
            self._pressed = False
            # Restore normal style
            self._apply_normal_style()

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
