"""Script card widget - entire card is clickable to execute scripts."""

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

# ----- Utils Modules -----
from src.utils import THEME_TEXT_PRIMARY, AccentTheme, get_icon


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
        self.setFixedHeight(32)
        self.setFrameShape(QFrame.Shape.NoFrame)
        # Ensure child widgets aren't clipped
        self.setAttribute(Qt.WidgetAttribute.WA_OpaquePaintEvent, False)

        self.name: str = name
        self._pressed = False

        # Use shared accent theme, initialize it once on first instance
        if ScriptRow._shared_color_theme is None:
            ScriptRow._shared_color_theme = AccentTheme.get()
        self.color_theme: dict[str, str] = ScriptRow._shared_color_theme

        # Main vertical layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(8, 6, 8, 6)
        main_layout.setSpacing(0)

        # Icon and name row
        name_row = QHBoxLayout()
        name_row.setSpacing(6)

        # Icon
        icon_label = QLabel()
        icon_label.setPixmap(get_icon(icon_name).pixmap(QSize(14, 14)))
        icon_label.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        icon_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        name_row.addWidget(icon_label)

        # Title label with inline badge
        if script_type:
            title_html: str = (
                f"{name} "
                f'<span style="color: {self.color_theme["border"]}; '
                f'font-size: 9pt; font-weight: bold;">'
                f"[{script_type[0].upper()}]</span>"
            )
        else:
            title_html = name

        self.title_label = QLabel(title_html, self)
        self.title_label.setProperty("CardTitle", True)
        self.title_label.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.title_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        name_row.addWidget(self.title_label)
        name_row.addStretch()

        main_layout.addLayout(name_row)

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
                color: {THEME_TEXT_PRIMARY};
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
                color: {THEME_TEXT_PRIMARY};
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
