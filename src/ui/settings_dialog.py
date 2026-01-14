"""
Settings dialog for configuring Obsidian Forge application.
Styled with Tokyo Night theme following GitUI's design patterns.
"""

# ----- PySide6 Modules-----
from PySide6.QtCore import QEvent, Qt
from PySide6.QtGui import QCursor, QFont, QKeySequence
from PySide6.QtWidgets import (
    QDialog,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

# ----- Core Modules-----
from src.core.config import (
    APP_NAME,
    FONT_FAMILY,
    FONT_SIZE_TEXT,
    PADDING,
    PADDING_LARGE,
    SPACING,
    SPACING_LARGE,
    SPACING_SMALL,
    Config,
)

# ----- Utils Modules-----
from src.utils import (
    COLOR_DARK_BLUE,
    COLOR_ORANGE,
    COLOR_PENDING,
    THEME_TEXT_PRIMARY,
    Icons,
)


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


class SettingsDialog(QDialog):
    """Dialog for configuring application settings."""

    def __init__(self, config: Config, parent=None) -> None:
        super().__init__(parent)
        self.config: Config = config
        self.setWindowTitle(f"Settings - {APP_NAME}")
        self.setMinimumWidth(700)
        self.setMinimumHeight(500)

        self.setup_ui()
        self.load_settings()

    def setup_ui(self) -> None:
        """Setup the user interface."""
        layout = QVBoxLayout()
        layout.setContentsMargins(
            PADDING_LARGE,
            PADDING_LARGE,
            PADDING_LARGE,
            PADDING_LARGE,
        )
        layout.setSpacing(SPACING_LARGE + 4)

        # Vault Path Section
        vault_group = QGroupBox(f"{Icons.SHIELD_LOCK} Obsidian Vault")
        vault_layout = QFormLayout()
        vault_layout.setSpacing(SPACING)
        vault_layout.setContentsMargins(PADDING, SPACING_LARGE + 4, PADDING, PADDING)

        vault_path_layout = QHBoxLayout()
        vault_path_layout.setSpacing(SPACING_SMALL)
        self.vault_path_input = QLineEdit()
        self.vault_path_input.setPlaceholderText("Path to your Obsidian vault")
        vault_browse_btn = HoverIconButton(
            normal_icon=Icons.FOLDER_OUTLINE,
            hover_icon=Icons.FOLDER,
            pressed_icon=Icons.FOLDER_OPEN,
            text="  &Browse",
        )
        vault_browse_btn.setProperty("Vault", True)
        vault_browse_btn.setFixedHeight(32)
        vault_browse_btn.setStyleSheet(
            f"""
            QPushButton[Vault=true] {{
                background-color: rgba(255, 255, 255, 0.04);
                color: {THEME_TEXT_PRIMARY};
                border-radius: 4px;
                padding: 4px 12px;
            }}
            QPushButton[Vault=true]:hover {{
                background-color: rgba(255, 255, 255, 0.08);
                border-bottom: 2px solid {COLOR_DARK_BLUE};
            }}
            QPushButton[Vault=true]:pressed {{
                background-color: rgba(255, 255, 255, 0.12);
            }}
            QPushButton[Vault=true]:focus {{
                background-color: rgba(255, 255, 255, 0.08);
                border-bottom: 2px solid {COLOR_DARK_BLUE};
                outline: none;
            }}
            """
        )
        vault_browse_btn.clicked.connect(self.browse_vault_path)
        vault_path_layout.addWidget(self.vault_path_input, 1)
        vault_path_layout.addWidget(vault_browse_btn)

        vault_layout.addRow("Vault Path:", vault_path_layout)

        vault_info = QLabel(
            "The vault should contain:\n"
            "  • 98 - Organize/Scripts/Add to Daily Note/\n"
            "  • 98 - Organize/Scripts/Add to Weekly Note/\n"
            "  • 98 - Organize/Scripts/Utils/"
        )
        vault_info.setProperty("InfoLabel", True)
        vault_layout.addRow("", vault_info)

        vault_group.setLayout(vault_layout)
        layout.addWidget(vault_group)

        # Node.js Path Section
        nodejs_group = QGroupBox(f"{Icons.NODE_JS} Node.js")
        nodejs_layout = QFormLayout()
        nodejs_layout.setSpacing(SPACING)
        nodejs_layout.setContentsMargins(PADDING, SPACING_LARGE + 4, PADDING, PADDING)

        nodejs_path_layout = QHBoxLayout()
        nodejs_path_layout.setSpacing(SPACING_SMALL)
        self.nodejs_path_input = QLineEdit()
        self.nodejs_path_input.setPlaceholderText("node (or full path to node.exe)")
        nodejs_browse_btn = HoverIconButton(
            normal_icon=Icons.FOLDER_OUTLINE,
            hover_icon=Icons.FOLDER,
            pressed_icon=Icons.FOLDER_OPEN,
            text="  B&rowse",
        )
        nodejs_browse_btn.setStyleSheet(
            f"""
            QPushButton {{
                background-color: rgba(255, 255, 255, 0.04);
                color: {THEME_TEXT_PRIMARY};
                border-radius: 4px;
                padding: 4px 12px;
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
            """
        )
        nodejs_browse_btn.setFixedHeight(32)
        nodejs_browse_btn.clicked.connect(self.browse_nodejs_path)
        nodejs_path_layout.addWidget(self.nodejs_path_input, 1)
        nodejs_path_layout.addWidget(nodejs_browse_btn)

        nodejs_layout.addRow("Node.js Path:", nodejs_path_layout)

        nodejs_info = QLabel(
            "Leave as 'node' if Node.js is in your PATH.\n"
            "Otherwise, specify the full path to node.exe"
        )
        nodejs_info.setProperty("InfoLabel", True)
        nodejs_layout.addRow("", nodejs_info)

        nodejs_group.setLayout(nodejs_layout)
        layout.addWidget(nodejs_group)

        layout.addStretch()

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(SPACING)
        button_layout.addStretch()

        validate_btn = HoverIconButton(
            normal_icon=Icons.VALIDATE_HOVER,
            hover_icon=Icons.VALIDATE_NORMAL,
            pressed_icon=Icons.VALIDATE_PRESSED,
            text="&Validate",
        )
        validate_btn.setFont(QFont(FONT_FAMILY, FONT_SIZE_TEXT))
        validate_btn.setFixedHeight(36)
        validate_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        validate_btn.setStyleSheet(
            f"""
            QPushButton {{
                background-color: rgba(255, 158, 100, 0.08);
                color: {COLOR_ORANGE};
                border-radius: 4px;
                padding: 4px 12px;
            }}
            QPushButton:hover {{
                background-color: rgba(255, 158, 100, 0.12);
                border-bottom: 2px solid {COLOR_ORANGE};
            }}
            QPushButton:pressed {{
                background-color: rgba(255, 158, 100, 0.16);
            }}
            QPushButton:focus {{
                background-color: rgba(255, 158, 100, 0.12);
                border-bottom: 2px solid {COLOR_ORANGE};
                outline: none;
            }}
            """
        )
        validate_btn.setShortcut(QKeySequence("Ctrl+T"))
        validate_btn.clicked.connect(self.validate_settings)
        button_layout.addWidget(validate_btn)

        # Save button
        save_btn = HoverIconButton(
            normal_icon=Icons.SAVE,
            hover_icon=Icons.CONTENT_SAVE,
            pressed_icon=Icons.CONTENT_SAVE_CHECK,
            text="&Save",
        )
        save_btn.setFont(QFont(FONT_FAMILY, FONT_SIZE_TEXT))
        save_btn.setFixedHeight(36)
        save_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        save_btn.setStyleSheet(
            f"""
            QPushButton {{
                background-color: rgba(158, 206, 106, 0.2);
                color: #9ece6a;
                border-radius: 4px;
                padding: 6px 16px;
            }}
            QPushButton:hover {{
                background-color: rgba(158, 206, 106, 0.3);
                border-bottom: 2px solid #9ece6a;
            }}
            QPushButton:pressed {{
                background-color: rgba(158, 206, 106, 0.4);
            }}
            QPushButton:focus {{
                background-color: rgba(158, 206, 106, 0.3);
                border-bottom: 2px solid #9ece6a;
                outline: none;
            }}
            """
        )
        save_btn.setDefault(True)
        save_btn.setShortcut(QKeySequence("Ctrl+Return"))
        save_btn.clicked.connect(self.save_settings)
        button_layout.addWidget(save_btn)

        # Cancel button
        cancel_btn = HoverIconButton(
            normal_icon=Icons.CANCEL_OUTLINE, hover_icon=Icons.CANCEL, text="&Cancel"
        )
        cancel_btn.setFont(QFont(FONT_FAMILY, FONT_SIZE_TEXT))
        cancel_btn.setShortcut(QKeySequence("Esc"))
        cancel_btn.setFixedHeight(36)
        cancel_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        cancel_btn.setStyleSheet(
            f"""
            QPushButton {{
                background-color: rgba(255, 255, 255, 0.04);
                color: {THEME_TEXT_PRIMARY};
                border-radius: 4px;
                padding: 6px 16px;
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
            """
        )
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)

        self.setLayout(layout)

    def load_settings(self) -> None:
        """Load current settings into the form."""
        self.vault_path_input.setText(self.config.vault_path)
        self.nodejs_path_input.setText(self.config.nodejs_path)
        self.vault_path_input.setFocus()

    def browse_vault_path(self) -> None:
        """Open file dialog to select vault path."""
        path: str = QFileDialog.getExistingDirectory(
            self, "Select Obsidian Vault Directory", self.vault_path_input.text() or ""
        )
        if path:
            self.vault_path_input.setText(path)

    def browse_nodejs_path(self) -> None:
        """Open file dialog to select Node.js executable."""
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Node.js Executable",
            "",
            "Executable Files (*.exe);;All Files (*.*)",
        )
        if path:
            self.nodejs_path_input.setText(path)

    def validate_settings(self) -> None:
        """Validate the current settings."""
        original_vault: str = self.config.vault_path
        original_nodejs: str = self.config.nodejs_path

        self.config.vault_path = self.vault_path_input.text()
        self.config.nodejs_path = self.nodejs_path_input.text()

        errors: list[str] = self.config.validate_paths()

        self.config.vault_path = original_vault
        self.config.nodejs_path = original_nodejs

        if errors:
            QMessageBox.warning(
                self,
                "Validation Failed",
                "The following issues were found:\n"
                + "\n".join(f"• {err}" for err in errors),
            )
        else:
            QMessageBox.information(
                self,
                "Validation Successful",
                "All settings are valid!",
            )

    def save_settings(self) -> None:
        """Save the settings and close the dialog."""
        self.config.vault_path = self.vault_path_input.text()
        self.config.nodejs_path = self.nodejs_path_input.text()

        if self.config.save_settings():
            errors: list[str] = self.config.validate_paths()
            if errors:
                QMessageBox.warning(
                    self,
                    "Settings Saved with Warnings",
                    "Settings saved, but there are issues:\n"
                    + "\n".join(f"• {err}" for err in errors),
                )
            self.accept()
        else:
            QMessageBox.critical(self, "Error", "Failed to save settings")
