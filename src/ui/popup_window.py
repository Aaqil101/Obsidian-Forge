"""
Popup window component for Obsidian Forge.
Styled with Tokyo Night theme, adapted from Blender-Launcher-V2 popup design.
"""

# ----- Built-In Modules -----
import textwrap
from enum import Enum
from typing import Optional

# ----- PySide6 Modules -----
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

# ----- Core Modules -----
from src.core import (
    BORDER_RADIUS_SMALL,
    FONT_FAMILY,
    FONT_SIZE_TEXT,
    PADDING_SMALL,
    SPACING_SMALL,
)

# ----- Utils Modules -----
from src.utils import get_icon


class PopupIcon(Enum):
    """Icon types for popup windows."""

    WARNING = "exclamation.svg"
    INFO = "info.svg"
    ERROR = "error.svg"
    SUCCESS = "check.svg"
    NONE = None


class PopupWindow(QDialog):
    """
    Custom popup dialog with Tokyo Night theme styling.

    Signals:
        accepted: Emitted when OK/accept button is clicked
        cancelled: Emitted when Cancel button is clicked
        custom_signal: Emitted with button label when custom button is clicked
    """

    accepted = Signal()
    cancelled = Signal()
    custom_signal = Signal(str)

    def __init__(
        self,
        message: str,
        title: str = "Info",
        info_popup: bool = False,
        icon: PopupIcon = PopupIcon.INFO,
        buttons: list[str] | None = None,
        parent: QWidget | None = None,
    ):
        """
        Create a popup dialog.

        Args:
            message: The message to display in the popup
            title: The title of the popup window (default: "Info")
            info_popup: If True, only shows OK button (default: False)
            icon: Icon to display (use PopupIcon enum)
            buttons: Optional list of button labels. If not provided:
                    - info_popup=True: Shows only OK
                    - info_popup=False: Shows OK and Cancel
            parent: Parent widget (optional)
        """
        super().__init__(parent)

        self.title = title
        self.message = message
        self.info_popup = info_popup
        self.buttons = buttons

        # Configure dialog
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.setWindowTitle(self.title)
        self.setMinimumSize(300, 150)

        # Remove minimize and maximize buttons
        self.setWindowFlags(
            self.windowFlags()
            & ~Qt.WindowType.WindowMinimizeButtonHint
            & ~Qt.WindowType.WindowMaximizeButtonHint
        )

        self._setup_ui(icon)
        self.adjustSize()
        self.setFixedSize(self.size())

    def _setup_ui(self, icon: PopupIcon) -> None:
        """Setup the popup UI."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(
            PADDING_SMALL, PADDING_SMALL, PADDING_SMALL, PADDING_SMALL
        )
        main_layout.setSpacing(SPACING_SMALL)

        # Icon and message layout
        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(4, 4, 6, 0)
        content_layout.setSpacing(SPACING_SMALL)

        # Icon
        if icon != PopupIcon.NONE:
            icon_label = QLabel()
            icon_label.setScaledContents(True)
            icon_label.setFixedSize(24, 24)
            icon_label.setPixmap(get_icon(icon.value).pixmap(24, 24))
            content_layout.addWidget(icon_label)

        # Wrap message text manually (similar to Blender-Launcher approach)
        wrapped_lines = []
        for line in self.message.splitlines():
            if not line.strip():
                wrapped_lines.append("")
            else:
                wrapped = textwrap.wrap(line, width=70)
                wrapped_lines.extend(wrapped)
        wrapped_message = "\n".join(wrapped_lines)

        message_label = QLabel(wrapped_message)
        message_label.setWordWrap(True)
        content_layout.addWidget(message_label)

        main_layout.addLayout(content_layout)
        main_layout.addSpacing(8)

        # Add buttons
        self._add_buttons(main_layout)

    def _add_buttons(self, layout: QVBoxLayout) -> None:
        """Add appropriate buttons based on configuration."""
        if self.buttons:
            self._add_custom_buttons(layout)
        elif self.info_popup:
            self._add_info_button(layout)
        else:
            self._add_default_buttons(layout)

    def _add_custom_buttons(self, layout: QVBoxLayout) -> None:
        """Add custom buttons based on provided list."""
        if self.buttons is None:
            return

        button_layout = QHBoxLayout()
        button_layout.setSpacing(SPACING_SMALL)

        if len(self.buttons) > 2:
            # Multiple custom buttons - emit custom_signal
            for label in self.buttons:
                button = self._create_button(label, self._custom_signal)
                button_layout.addWidget(button)
        elif len(self.buttons) == 2:
            # Two buttons: OK and Cancel
            ok_button = self._create_button(self.buttons[0], self._accept, primary=True)
            cancel_button = self._create_button(
                self.buttons[1], self._cancel, cancel=True
            )
            button_layout.addWidget(ok_button)
            button_layout.addWidget(cancel_button)
        else:
            # Single button: OK
            ok_button = self._create_button(self.buttons[0], self._accept, primary=True)
            button_layout.addWidget(ok_button)

        layout.addLayout(button_layout)

    def _add_info_button(self, layout: QVBoxLayout) -> None:
        """Add single OK button for info popup."""
        button_layout = QHBoxLayout()
        button_layout.setSpacing(SPACING_SMALL)
        button_layout.addStretch()

        ok_button = self._create_button("OK", self._accept, primary=True)
        button_layout.addWidget(ok_button)

        layout.addLayout(button_layout)

    def _add_default_buttons(self, layout: QVBoxLayout) -> None:
        """Add default OK and Cancel buttons."""
        button_layout = QHBoxLayout()
        button_layout.setSpacing(SPACING_SMALL)
        button_layout.addStretch()

        ok_button = self._create_button("OK", self._accept, primary=True)
        cancel_button = self._create_button("Cancel", self._cancel, cancel=True)

        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)

        layout.addLayout(button_layout)

    def _create_button(
        self,
        label: str,
        callback,
        primary: bool = False,
        cancel: bool = False,
    ) -> QPushButton:
        """Create a button with appropriate styling."""
        button = QPushButton(label)
        button.setProperty("Popup", True)

        if primary:
            button.setProperty("PrimaryButton", True)
        elif cancel:
            button.setProperty("CancelButton", True)

        # Connect callback
        if callback == self._custom_signal:
            button.clicked.connect(lambda: callback(label))
        else:
            button.clicked.connect(callback)

        return button

    def _custom_signal(self, label: str) -> None:
        """Emit custom signal and close."""
        self.custom_signal.emit(label)
        self.accept()

    def _accept(self) -> None:
        """Emit accepted signal and close."""
        self.accepted.emit()
        self.accept()

    def _cancel(self) -> None:
        """Emit cancelled signal and close."""
        self.cancelled.emit()
        self.reject()

    def keyPressEvent(self, event: QKeyEvent) -> None:
        """Handle keyboard events."""
        if event.key() == Qt.Key.Key_Escape and not self.info_popup:
            self._cancel()
        elif event.key() in {Qt.Key.Key_Return, Qt.Key.Key_Enter}:
            self._accept()
        else:
            super().keyPressEvent(event)
