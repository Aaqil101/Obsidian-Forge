"""
Settings dialog for configuring Obsidian Forge application.
Styled with Tokyo Night theme following GitUI's design patterns.
"""

# ----- Built-In Modules-----
from pathlib import Path

# ----- PySide6 Modules-----
from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QCursor, QFont, QKeySequence
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

# ----- Core Modules-----
from src.core.config import (
    APP_NAME,
    FONT_FAMILY,
    FONT_SIZE_TEXT,
    PADDING_SMALL,
    SPACING,
    SPACING_SMALL,
    Config,
)

# ----- UI Modules-----
from src.ui.widgets import SettingsGroup

# ----- Utils Modules-----
from src.utils import COLOR_ORANGE, THEME_TEXT_PRIMARY, HoverIconButton, Icons, get_icon


class SettingsDialog(QDialog):
    """Dialog for configuring application settings."""

    def __init__(self, config: Config, parent=None) -> None:
        super().__init__(parent)
        self.config: Config = config
        self.setWindowTitle(f"Settings - {APP_NAME}")
        self.setMinimumWidth(700)
        self.setMinimumHeight(630)

        # Store comboboxes for path selection
        self.daily_path_combo: QComboBox = None
        self.weekly_path_combo: QComboBox = None
        self.utils_path_combo: QComboBox = None
        self.time_path_combo: QComboBox = None

        self.setup_ui()
        self.load_settings()

    def setup_ui(self) -> None:
        """Setup the user interface with card-based collapsible sections."""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(
            PADDING_SMALL, PADDING_SMALL, PADDING_SMALL, PADDING_SMALL
        )
        main_layout.setSpacing(SPACING_SMALL)

        # Scroll area for settings content
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)

        # Container for all sections
        sections_container = QWidget()
        sections_layout = QVBoxLayout(sections_container)
        sections_layout.setContentsMargins(0, 0, 0, 0)
        sections_layout.setSpacing(0)

        # === Obsidian Vault Section ===
        vault_section = SettingsGroup("Obsidian Vault", parent=sections_container)

        vault_content = QWidget()
        vault_content_layout = QVBoxLayout(vault_content)
        vault_content_layout.setContentsMargins(8, 8, 8, 8)
        vault_content_layout.setSpacing(SPACING)

        # Vault path row with icon
        vault_path_row = QWidget()
        vault_path_layout = QHBoxLayout(vault_path_row)
        vault_path_layout.setContentsMargins(0, 0, 0, 0)
        vault_path_layout.setSpacing(SPACING_SMALL)

        # Obsidian icon
        vault_icon_label = QLabel()
        vault_icon_label.setPixmap(get_icon("obsidian.svg").pixmap(QSize(20, 20)))
        vault_icon_label.setFixedSize(20, 20)
        vault_path_layout.addWidget(vault_icon_label)

        # Vault path input
        self.vault_path_input = QLineEdit()
        self.vault_path_input.setProperty("MainLineEdit", True)
        self.vault_path_input.setPlaceholderText("Path to your Obsidian vault")
        vault_path_layout.addWidget(self.vault_path_input, 1)

        # Browse button
        vault_browse_btn = HoverIconButton(
            normal_icon=Icons.FOLDER_OUTLINE,
            hover_icon=Icons.FOLDER,
            pressed_icon=Icons.FOLDER_OPEN,
            text="  &Browse",
        )
        vault_browse_btn.setProperty("BrowseButton", True)
        vault_browse_btn.setFixedHeight(32)
        vault_browse_btn.clicked.connect(self.browse_vault_path)
        vault_path_layout.addWidget(vault_browse_btn)

        vault_content_layout.addWidget(vault_path_row)

        # Connect vault path input to auto-scan
        self.vault_path_input.textChanged.connect(self._on_vault_path_changed)

        # Separator line
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet(
            "background-color: rgba(192, 202, 245, 0.1); margin: 8px 0px;"
        )
        separator.setFixedHeight(1)
        vault_content_layout.addWidget(separator)

        # Script Paths label (compact)
        script_paths_label = QLabel("Script Paths:")
        script_paths_label.setFont(QFont(FONT_FAMILY, FONT_SIZE_TEXT - 1))
        script_paths_label.setStyleSheet(
            "color: rgba(192, 202, 245, 0.7); padding-left: 8px;"
        )
        vault_content_layout.addWidget(script_paths_label)

        # Compact path rows
        daily_path_row = self._create_path_combobox_row("Daily:", "daily")
        vault_content_layout.addWidget(daily_path_row)

        weekly_path_row = self._create_path_combobox_row("Weekly:", "weekly")
        vault_content_layout.addWidget(weekly_path_row)

        utils_path_row = self._create_path_combobox_row("Utils:", "utils")
        vault_content_layout.addWidget(utils_path_row)

        time_path_row = self._create_path_combobox_row("Time:", "time")
        vault_content_layout.addWidget(time_path_row)

        # Compact info label
        script_paths_info = QLabel("Select custom paths or leave as (Default)")
        script_paths_info.setFont(QFont(FONT_FAMILY, FONT_SIZE_TEXT - 2))
        script_paths_info.setStyleSheet(
            "color: rgba(192, 202, 245, 0.5); padding-left: 8px;"
        )
        vault_content_layout.addWidget(script_paths_info)

        vault_section.setWidget(vault_content)
        sections_layout.addWidget(vault_section)

        # === Node.js Section ===
        nodejs_section = SettingsGroup("Node.js", parent=sections_container)

        nodejs_content = QWidget()
        nodejs_content_layout = QVBoxLayout(nodejs_content)
        nodejs_content_layout.setContentsMargins(8, 8, 8, 8)
        nodejs_content_layout.setSpacing(SPACING)

        # Node.js path row with icon
        nodejs_path_row = QWidget()
        nodejs_path_layout = QHBoxLayout(nodejs_path_row)
        nodejs_path_layout.setContentsMargins(0, 0, 0, 0)
        nodejs_path_layout.setSpacing(SPACING_SMALL)

        # Node.js icon
        nodejs_icon_label = QLabel()
        nodejs_icon_label.setPixmap(
            get_icon("nodejs.svg", color=f"{COLOR_ORANGE}").pixmap(QSize(20, 20))
        )
        nodejs_icon_label.setFixedSize(20, 20)
        nodejs_path_layout.addWidget(nodejs_icon_label)

        # Node.js path input
        self.nodejs_path_input = QLineEdit()
        self.nodejs_path_input.setProperty("MainLineEdit", True)
        self.nodejs_path_input.setPlaceholderText("node (or full path to node.exe)")
        nodejs_path_layout.addWidget(self.nodejs_path_input, 1)

        # Browse button
        nodejs_browse_btn = HoverIconButton(
            normal_icon=Icons.FOLDER_OUTLINE,
            hover_icon=Icons.FOLDER,
            pressed_icon=Icons.FOLDER_OPEN,
            text="  B&rowse",
        )
        nodejs_browse_btn.setProperty("BrowseButton", True)
        nodejs_browse_btn.setFixedHeight(32)
        nodejs_browse_btn.clicked.connect(self.browse_nodejs_path)
        nodejs_path_layout.addWidget(nodejs_browse_btn)

        nodejs_content_layout.addWidget(nodejs_path_row)

        # Node.js info
        nodejs_info = QLabel(
            "Leave as 'node' if Node.js is in your PATH.\n"
            "Otherwise, specify the full path to node.exe"
        )
        nodejs_info.setProperty("InfoLabel", True)
        nodejs_info.setFont(QFont(FONT_FAMILY, FONT_SIZE_TEXT - 1))
        nodejs_info.setStyleSheet(
            "color: rgba(192, 202, 245, 0.6); padding-left: 28px;"
        )
        nodejs_content_layout.addWidget(nodejs_info)

        nodejs_section.setWidget(nodejs_content)
        sections_layout.addWidget(nodejs_section)

        # === Scan Settings Section ===
        scan_section = SettingsGroup("Scan Settings", parent=sections_container)

        scan_content = QWidget()
        scan_content_layout = QVBoxLayout(scan_content)
        scan_content_layout.setContentsMargins(8, 8, 8, 8)
        scan_content_layout.setSpacing(SPACING)

        # Excluded directories row
        excluded_dirs_row = QWidget()
        excluded_dirs_layout = QHBoxLayout(excluded_dirs_row)
        excluded_dirs_layout.setContentsMargins(0, 0, 0, 0)
        excluded_dirs_layout.setSpacing(SPACING_SMALL)

        # Icon label using SVG
        icon_label = QLabel()
        icon_label.setPixmap(
            get_icon("exclude.svg", color=f"{COLOR_ORANGE}").pixmap(QSize(20, 20))
        )
        icon_label.setFixedSize(20, 20)
        excluded_dirs_layout.addWidget(icon_label)

        # Description label
        desc_label = QLabel("Excluded Directories")
        desc_label.setFont(QFont(FONT_FAMILY, FONT_SIZE_TEXT))
        desc_label.setStyleSheet(f"color: {THEME_TEXT_PRIMARY};")
        excluded_dirs_layout.addWidget(desc_label)

        excluded_dirs_layout.addStretch()

        # Manage button
        manage_excluded_btn = HoverIconButton(
            normal_icon=Icons.SETTINGS,
            hover_icon=Icons.COG,
            pressed_icon=Icons.ADVANCED,
            text="&Manage",
        )
        manage_excluded_btn.setFont(QFont(FONT_FAMILY, FONT_SIZE_TEXT))
        manage_excluded_btn.setProperty("BrowseButton", True)
        manage_excluded_btn.setFixedHeight(32)
        manage_excluded_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        manage_excluded_btn.clicked.connect(self.open_excluded_dirs_manager)
        excluded_dirs_layout.addWidget(manage_excluded_btn)

        scan_content_layout.addWidget(excluded_dirs_row)

        # Info label
        excluded_dirs_info = QLabel(
            "Manage directory names to exclude from vault scans.\n"
            "These directories will be hidden from folder searches and file scans."
        )
        excluded_dirs_info.setFont(QFont(FONT_FAMILY, FONT_SIZE_TEXT - 1))
        excluded_dirs_info.setStyleSheet(
            "color: rgba(192, 202, 245, 0.6); padding-left: 28px;"
        )
        scan_content_layout.addWidget(excluded_dirs_info)

        scan_section.setWidget(scan_content)
        sections_layout.addWidget(scan_section)

        sections_layout.addStretch()

        scroll_area.setWidget(sections_container)
        main_layout.addWidget(scroll_area)

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
        validate_btn.setProperty("ValidateButton", True)
        validate_btn.setFixedHeight(36)
        validate_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
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
        save_btn.setProperty("SaveButton", True)
        save_btn.setFixedHeight(36)
        save_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        save_btn.setDefault(True)
        save_btn.setShortcut(QKeySequence("Ctrl+Return"))
        save_btn.clicked.connect(self.save_settings)
        button_layout.addWidget(save_btn)

        # Cancel button
        cancel_btn = HoverIconButton(
            normal_icon=Icons.CANCEL_OUTLINE, hover_icon=Icons.CANCEL, text="&Cancel"
        )
        cancel_btn.setFont(QFont(FONT_FAMILY, FONT_SIZE_TEXT))
        cancel_btn.setProperty("CancelButton", True)
        cancel_btn.setShortcut(QKeySequence("Esc"))
        cancel_btn.setFixedHeight(36)
        cancel_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

    def _create_path_combobox_row(self, label_text: str, path_type: str) -> QWidget:
        """Create a compact row with label and combobox for path selection.

        Args:
            label_text: The label text to display
            path_type: The type of path (daily, weekly, utils, time)

        Returns:
            QWidget containing the row layout
        """
        row = QWidget()
        layout = QHBoxLayout(row)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING_SMALL)

        # Indent spacer
        indent = QLabel()
        indent.setFixedWidth(20)
        layout.addWidget(indent)

        # Label (compact)
        label = QLabel(label_text)
        label.setFont(QFont(FONT_FAMILY, FONT_SIZE_TEXT - 1))
        label.setStyleSheet("color: rgba(192, 202, 245, 0.7);")
        label.setMinimumWidth(60)
        label.setMaximumWidth(60)
        layout.addWidget(label)

        # ComboBox (compact)
        combo = QComboBox()
        combo.setFont(QFont(FONT_FAMILY, FONT_SIZE_TEXT - 1))
        combo.setMinimumHeight(26)
        combo.setMaximumHeight(26)
        combo.addItem("(Default)")
        combo.setEnabled(False)

        layout.addWidget(combo, 1)

        # Store reference to combobox
        if path_type == "daily":
            self.daily_path_combo = combo
        elif path_type == "weekly":
            self.weekly_path_combo = combo
        elif path_type == "utils":
            self.utils_path_combo = combo
        elif path_type == "time":
            self.time_path_combo = combo

        return row

    def load_settings(self) -> None:
        """Load current settings into the form."""
        self.vault_path_input.setText(self.config.vault_path)
        self.nodejs_path_input.setText(self.config.nodejs_path)

        # Auto-scan vault if path exists
        if self.config.vault_path and Path(self.config.vault_path).exists():
            self._auto_scan_vault(self.config.vault_path)

        # Load custom paths if set
        if self.config.custom_daily_scripts_path:
            self._set_combobox_value(
                self.daily_path_combo, self.config.custom_daily_scripts_path
            )
        if self.config.custom_weekly_scripts_path:
            self._set_combobox_value(
                self.weekly_path_combo, self.config.custom_weekly_scripts_path
            )
        if self.config.custom_utils_scripts_path:
            self._set_combobox_value(
                self.utils_path_combo, self.config.custom_utils_scripts_path
            )
        if self.config.custom_time_path:
            self._set_combobox_value(self.time_path_combo, self.config.custom_time_path)

        self.vault_path_input.setFocus()

    def _set_combobox_value(self, combo: QComboBox, value: str) -> None:
        """Set the combobox to a specific value, adding it if not present."""
        if not combo or not value:
            return

        # Check if value exists in combobox
        index: int = combo.findText(value)
        if index >= 0:
            combo.setCurrentIndex(index)
        else:
            # Add the value and select it
            combo.addItem(value)
            combo.setCurrentText(value)

    def browse_vault_path(self) -> None:
        """Open file dialog to select vault path."""
        path: str = QFileDialog.getExistingDirectory(
            self, "Select Obsidian Vault Directory", self.vault_path_input.text() or ""
        )
        if path:
            # Auto-scan will be triggered by textChanged signal
            self.vault_path_input.setText(path)

    def _on_vault_path_changed(self, path: str) -> None:
        """Handle vault path changes and auto-scan."""
        if path and Path(path).exists():
            self._auto_scan_vault(path)

    def _auto_scan_vault(self, vault_path: str) -> None:
        """Silently scan the vault and populate dropdowns without showing messages."""
        # Scan vault folders (already filters excluded directories)
        folders: list[str] = self.config.scan_vault_folders(vault_path)

        # Get markdown files for the time path
        vault_root = Path(vault_path)
        files = []
        excluded: list[str] = self.config.excluded_directories

        # Recursively find all .md files, excluding configured directories
        for md_file in vault_root.rglob("*.md"):
            # Get relative path from vault root
            try:
                rel_path: Path = md_file.relative_to(vault_root)
                rel_path_str: str = str(rel_path).replace("\\", "/")

                # Skip files in excluded directories (check both folder names and full paths)
                should_exclude = False
                path_parts = rel_path.parts

                for part in path_parts[:-1]:  # Check all parts except the filename
                    if part in excluded:
                        should_exclude = True
                        break

                # Also check if any parent path matches excluded full paths
                if not should_exclude:
                    current_check = ""
                    for part in path_parts[:-1]:
                        current_check = (
                            f"{current_check}/{part}" if current_check else part
                        )
                        if current_check in excluded:
                            should_exclude = True
                            break

                if should_exclude:
                    continue

                files.append(rel_path_str)
            except ValueError:
                continue

        # Populate comboboxes silently
        self._populate_combobox(self.daily_path_combo, folders)
        self._populate_combobox(self.weekly_path_combo, folders)
        self._populate_combobox(self.utils_path_combo, folders)
        self._populate_combobox(self.time_path_combo, sorted(files))

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

    def open_excluded_dirs_manager(self) -> None:
        """Open the excluded directories manager window."""
        from src.ui.excluded_dirs_manager import ExcludedDirsManager

        manager = ExcludedDirsManager(self.config, self)
        manager.exec()

    def _populate_combobox(self, combo: QComboBox, items: list[str]) -> None:
        """Populate a combobox with items while preserving current selection."""
        if not combo:
            return

        current_text: str = combo.currentText()
        combo.clear()
        combo.addItem("(Default)")

        for item in items:
            combo.addItem(item)

        # Enable the combobox now that it has items
        combo.setEnabled(True)

        # Restore previous selection if it exists
        if current_text and current_text != "(Default)":
            index: int = combo.findText(current_text)
            if index >= 0:
                combo.setCurrentIndex(index)

    def validate_settings(self) -> None:
        """Validate the current settings."""
        original_vault: str = self.config.vault_path
        original_nodejs: str = self.config.nodejs_path
        original_daily: str = self.config.custom_daily_scripts_path
        original_weekly: str = self.config.custom_weekly_scripts_path
        original_utils: str = self.config.custom_utils_scripts_path
        original_time: str = self.config.custom_time_path

        self.config.vault_path = self.vault_path_input.text()
        self.config.nodejs_path = self.nodejs_path_input.text()

        # Set custom paths for validation
        self.config.custom_daily_scripts_path = (
            ""
            if self.daily_path_combo.currentText() == "(Default)"
            else self.daily_path_combo.currentText()
        )
        self.config.custom_weekly_scripts_path = (
            ""
            if self.weekly_path_combo.currentText() == "(Default)"
            else self.weekly_path_combo.currentText()
        )
        self.config.custom_utils_scripts_path = (
            ""
            if self.utils_path_combo.currentText() == "(Default)"
            else self.utils_path_combo.currentText()
        )
        self.config.custom_time_path = (
            ""
            if self.time_path_combo.currentText() == "(Default)"
            else self.time_path_combo.currentText()
        )

        errors: list[str] = self.config.validate_paths()

        # Restore original values
        self.config.vault_path = original_vault
        self.config.nodejs_path = original_nodejs
        self.config.custom_daily_scripts_path = original_daily
        self.config.custom_weekly_scripts_path = original_weekly
        self.config.custom_utils_scripts_path = original_utils
        self.config.custom_time_path = original_time

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

        # Save custom paths (empty string if default is selected)
        self.config.custom_daily_scripts_path = (
            ""
            if self.daily_path_combo.currentText() == "(Default)"
            else self.daily_path_combo.currentText()
        )
        self.config.custom_weekly_scripts_path = (
            ""
            if self.weekly_path_combo.currentText() == "(Default)"
            else self.weekly_path_combo.currentText()
        )
        self.config.custom_utils_scripts_path = (
            ""
            if self.utils_path_combo.currentText() == "(Default)"
            else self.utils_path_combo.currentText()
        )
        self.config.custom_time_path = (
            ""
            if self.time_path_combo.currentText() == "(Default)"
            else self.time_path_combo.currentText()
        )

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
