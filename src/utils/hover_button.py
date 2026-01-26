# ----- PySide6 Modules-----
from PySide6.QtCore import QEvent, QSize
from PySide6.QtWidgets import QPushButton, QWidget

# ----- Utils Modules -----
from src.utils.color import THEME_TEXT_PRIMARY, THEME_TEXT_SECONDARY
from src.utils.resources import get_icon


class HoverIconButton(QPushButton):
    """QPushButton subclass that changes icon on hover and press states.

    This button displays different icons based on user interaction:
    - Normal state: Shows normal_icon
    - Hover state: Shows hover_icon
    - Pressed state: Shows pressed_icon (if provided, otherwise uses hover_icon)

    Args:
        normal_icon: Icon to display in normal state
        hover_icon: Icon to display on hover
        pressed_icon: Optional icon to display when pressed (defaults to hover_icon)
        text: Button text (default: empty string)
        parent: Parent widget (default: None)
    """

    def __init__(
        self,
        normal_icon: str,
        hover_icon: str,
        pressed_icon: str = "",
        text: str = "",
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(text, parent)
        self.normal_icon: str = normal_icon
        self.hover_icon: str = hover_icon
        self.pressed_icon: str = pressed_icon if pressed_icon else hover_icon
        self._is_hovered = False
        self._is_pressed = False

        # Set initial text with normal icon
        self._update_text()

        # Connect pressed/released signals for click state tracking
        self.pressed.connect(self._on_pressed)
        self.released.connect(self._on_released)

    def _update_text(self) -> None:
        """Update button text based on current state."""
        # Extract text without icon (text after " " if present)
        text_parts: list[str] = self.text().split(" ", 1)
        label_text: str = text_parts[1] if len(text_parts) > 1 else text_parts[0]

        # Determine which icon to show
        if self._is_pressed:
            icon: str = self.pressed_icon
        elif self._is_hovered:
            icon: str = self.hover_icon
        else:
            icon: str = self.normal_icon

        # Set text with icon (only if we have label text)
        if label_text and not label_text.startswith(
            (self.normal_icon, self.hover_icon, self.pressed_icon)
        ):
            self.setText(f"{icon} {label_text}")
        else:
            self.setText(icon)

    def enterEvent(self, event: QEvent) -> None:
        """Handle mouse enter event."""
        self._is_hovered = True
        self._update_text()
        super().enterEvent(event)

    def leaveEvent(self, event: QEvent) -> None:
        """Handle mouse leave event."""
        self._is_hovered = False
        self._is_pressed = False  # Reset pressed state when leaving
        self._update_text()
        super().leaveEvent(event)

    def _on_pressed(self) -> None:
        """Handle button pressed signal."""
        self._is_pressed = True
        self._update_text()

    def _on_released(self) -> None:
        """Handle button released signal."""
        self._is_pressed = False
        self._update_text()


class HoverIconButtonSVG(QPushButton):
    """QPushButton subclass that changes SVG icon on hover and press states.

    This button displays different SVG icons based on user interaction:
    - Normal state: Shows normal icon with normal_color
    - Hover state: Shows hover icon with hover_color
    - Pressed state: Shows pressed icon with pressed_color (if provided)

    Args:
        normal_icon: SVG filename for normal state (e.g., "close.svg")
        hover_icon: SVG filename for hover state (can be same as normal_icon)
        pressed_icon: Optional SVG filename for pressed state (defaults to hover_icon)
        normal_color: Hex color for normal state (e.g., "#7aa2f7")
        hover_color: Hex color for hover state (e.g., "#bb9af7")
        pressed_color: Optional hex color for pressed state (defaults to hover_color)
        icon_size: Icon size in pixels (default: 16)
        text: Button text (default: empty string)
        parent: Parent widget (default: None)
    """

    def __init__(
        self,
        normal_icon: str,
        hover_icon: str,
        pressed_icon: str = "",
        normal_color: str = f"{THEME_TEXT_PRIMARY}",
        hover_color: str = f"{THEME_TEXT_SECONDARY}",
        pressed_color: str = None,
        icon_size: int = 16,
        text: str = "",
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(text, parent)

        self.normal_icon_name: str = normal_icon
        self.hover_icon_name: str = hover_icon
        self.pressed_icon_name: str = pressed_icon if pressed_icon else hover_icon
        self.normal_color: str = normal_color
        self.hover_color: str = hover_color
        self.pressed_color: str = pressed_color if pressed_color else hover_color
        self.icon_size: int = icon_size
        self._is_hovered = False
        self._is_pressed = False

        # Load icons
        self.normal_icon = get_icon(self.normal_icon_name, color=self.normal_color)
        self.hover_icon = get_icon(self.hover_icon_name, color=self.hover_color)
        self.pressed_icon = get_icon(self.pressed_icon_name, color=self.pressed_color)

        # Set initial icon
        self.setIcon(self.normal_icon)
        self.setIconSize(QSize(self.icon_size, self.icon_size))

        # Connect pressed/released signals for click state tracking
        self.pressed.connect(self._on_pressed)
        self.released.connect(self._on_released)

    def _update_icon(self) -> None:
        """Update button icon based on current state."""
        if self._is_pressed:
            self.setIcon(self.pressed_icon)
        elif self._is_hovered:
            self.setIcon(self.hover_icon)
        else:
            self.setIcon(self.normal_icon)

    def enterEvent(self, event: QEvent) -> None:
        """Handle mouse enter event."""
        self._is_hovered = True
        self._update_icon()
        super().enterEvent(event)

    def leaveEvent(self, event: QEvent) -> None:
        """Handle mouse leave event."""
        self._is_hovered = False
        self._is_pressed = False  # Reset pressed state when leaving
        self._update_icon()
        super().leaveEvent(event)

    def _on_pressed(self) -> None:
        """Handle button pressed signal."""
        self._is_pressed = True
        self._update_icon()

    def _on_released(self) -> None:
        """Handle button released signal."""
        self._is_pressed = False
        self._update_icon()
