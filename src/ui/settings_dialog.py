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
    QCheckBox,
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
from src.core.config import APP_NAME, FONT_FAMILY, Config

# ----- UI Modules-----
from src.ui.widgets import SettingsGroup

# ----- Utils Modules-----
from src.utils import (
    COLOR_GREEN,
    COLOR_ORANGE,
    COLOR_PURPLE,
    COLOR_RED,
    THEME_TEXT_PRIMARY,
    AccentTheme,
    HoverIconButtonSVG,
    disable_autostart,
    enable_autostart,
    get_icon,
    is_autostart_enabled,
)


class SettingsDialog(QDialog):
    """Dialog for configuring application settings."""

    _shared_color_theme: dict[str, str] | None = None

    def __init__(self, config: Config, parent=None) -> None:
        super().__init__(parent)
        self.config: Config = config
        self.setWindowTitle(f"Settings - {APP_NAME}")
        self.setMinimumWidth(700)
        self.setMinimumHeight(630)

        # Use shared accent theme, initialize it once on first instance
        if SettingsDialog._shared_color_theme is None:
            SettingsDialog._shared_color_theme = AccentTheme.get()
        self.color_theme: dict[str, str] = SettingsDialog._shared_color_theme

        # Store comboboxes for path selection
        self.daily_path_combo: QComboBox = None
        self.daily_journal_combo: QComboBox = None
        self.weekly_path_combo: QComboBox = None
        self.weekly_journal_combo: QComboBox = None
        self.utils_path_combo: QComboBox = None
        self.time_path_combo: QComboBox = None

        # Store checkboxes for tray settings
        self.start_minimized_checkbox: QCheckBox = None
        self.autostart_checkbox: QCheckBox = None

        self.setup_ui()
        self.load_settings()

    def setup_ui(self) -> None:
        """Setup the user interface with card-based collapsible sections."""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(8)

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
        vault_content_layout.setSpacing(12)

        # Vault path row with icon
        vault_path_row = QWidget()
        vault_path_layout = QHBoxLayout(vault_path_row)
        vault_path_layout.setContentsMargins(0, 0, 0, 0)
        vault_path_layout.setSpacing(8)

        # Obsidian icon
        vault_icon_label = QLabel()
        vault_icon_label.setPixmap(
            get_icon(
                "application/obsidian.svg", color=self.color_theme["border"]
            ).pixmap(QSize(20, 20))
        )
        vault_icon_label.setFixedSize(20, 20)
        vault_path_layout.addWidget(vault_icon_label)

        # Vault path input
        self.vault_path_input = QLineEdit()
        self.vault_path_input.setProperty("MainLineEdit", True)
        self.vault_path_input.setPlaceholderText("Path to your Obsidian vault")
        vault_path_layout.addWidget(self.vault_path_input, 1)

        # Browse button
        vault_browse_btn = HoverIconButtonSVG(
            normal_icon="folder_outline.svg",
            normal_color=f"{THEME_TEXT_PRIMARY}",
            hover_icon="folder.svg",
            hover_color=f"{THEME_TEXT_PRIMARY}",
            pressed_icon="folder_open.svg",
            pressed_color=f"{THEME_TEXT_PRIMARY}",
            icon_size=14,
        )
        vault_browse_btn.setProperty("BrowseButton", True)
        vault_browse_btn.setShortcut(QKeySequence("Ctrl+Shift+B"))
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
        script_paths_label.setFont(QFont(FONT_FAMILY, 9))
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
        script_paths_info.setFont(QFont(FONT_FAMILY, 10 - 2))
        script_paths_info.setStyleSheet(
            "color: rgba(192, 202, 245, 0.5); padding-left: 8px;"
        )
        vault_content_layout.addWidget(script_paths_info)

        # Separator line
        separator2 = QFrame()
        separator2.setFrameShape(QFrame.Shape.HLine)
        separator2.setStyleSheet(
            "background-color: rgba(192, 202, 245, 0.1); margin: 8px 0px;"
        )
        separator2.setFixedHeight(1)
        vault_content_layout.addWidget(separator2)

        # Journal Paths label (compact)
        journal_paths_label = QLabel("Journal Paths:")
        journal_paths_label.setFont(QFont(FONT_FAMILY, 9))
        journal_paths_label.setStyleSheet(
            "color: rgba(192, 202, 245, 0.7); padding-left: 8px;"
        )
        vault_content_layout.addWidget(journal_paths_label)

        # Compact journal path rows
        daily_journal_row = self._create_path_combobox_row("Daily:", "daily_journal")
        vault_content_layout.addWidget(daily_journal_row)

        weekly_journal_row = self._create_path_combobox_row("Weekly:", "weekly_journal")
        vault_content_layout.addWidget(weekly_journal_row)

        # Compact info label for journal paths
        journal_paths_info = QLabel("Select journal folders or leave as (Default)")
        journal_paths_info.setFont(QFont(FONT_FAMILY, 10 - 2))
        journal_paths_info.setStyleSheet(
            "color: rgba(192, 202, 245, 0.5); padding-left: 8px;"
        )
        vault_content_layout.addWidget(journal_paths_info)

        vault_section.setWidget(vault_content)
        sections_layout.addWidget(vault_section)

        # === Node.js Section ===
        nodejs_section = SettingsGroup("Node.js", parent=sections_container)

        nodejs_content = QWidget()
        nodejs_content_layout = QVBoxLayout(nodejs_content)
        nodejs_content_layout.setContentsMargins(8, 8, 8, 8)
        nodejs_content_layout.setSpacing(12)

        # Node.js path row with icon
        nodejs_path_row = QWidget()
        nodejs_path_layout = QHBoxLayout(nodejs_path_row)
        nodejs_path_layout.setContentsMargins(0, 0, 0, 0)
        nodejs_path_layout.setSpacing(8)

        # Node.js icon
        nodejs_icon_label = QLabel()
        nodejs_icon_label.setPixmap(
            get_icon("application/nodejs.svg", color=self.color_theme["border"]).pixmap(
                QSize(20, 20)
            )
        )
        nodejs_icon_label.setFixedSize(20, 20)
        nodejs_path_layout.addWidget(nodejs_icon_label)

        # Node.js path input
        self.nodejs_path_input = QLineEdit()
        self.nodejs_path_input.setProperty("MainLineEdit", True)
        self.nodejs_path_input.setPlaceholderText("node (or full path to node.exe)")
        nodejs_path_layout.addWidget(self.nodejs_path_input, 1)

        # Browse button
        nodejs_browse_btn = HoverIconButtonSVG(
            normal_icon="folder_outline.svg",
            normal_color=f"{THEME_TEXT_PRIMARY}",
            hover_icon="folder.svg",
            hover_color=f"{THEME_TEXT_PRIMARY}",
            pressed_icon="folder_open.svg",
            pressed_color=f"{THEME_TEXT_PRIMARY}",
            icon_size=14,
        )
        nodejs_browse_btn.setProperty("BrowseButton", True)
        nodejs_browse_btn.setShortcut(QKeySequence("Ctrl+B"))
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
        nodejs_info.setFont(QFont(FONT_FAMILY, 9))
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
        scan_content_layout.setSpacing(12)

        # Excluded directories row
        excluded_dirs_row = QWidget()
        excluded_dirs_layout = QHBoxLayout(excluded_dirs_row)
        excluded_dirs_layout.setContentsMargins(0, 0, 0, 0)
        excluded_dirs_layout.setSpacing(8)

        # Icon label using SVG
        icon_label = QLabel()
        icon_label.setPixmap(
            get_icon("exclude.svg", color=self.color_theme["border"]).pixmap(
                QSize(20, 20)
            )
        )
        icon_label.setFixedSize(20, 20)
        excluded_dirs_layout.addWidget(icon_label)

        # Description label
        desc_label = QLabel("Excluded Directories")
        desc_label.setFont(QFont(FONT_FAMILY, 10))
        desc_label.setStyleSheet(f"color: {THEME_TEXT_PRIMARY};")
        excluded_dirs_layout.addWidget(desc_label)

        excluded_dirs_layout.addStretch()

        # Manage button
        manage_excluded_btn = HoverIconButtonSVG(
            normal_icon="settings_outline.svg",
            normal_color=f"{THEME_TEXT_PRIMARY}",
            hover_icon="settings.svg",
            hover_color=f"{THEME_TEXT_PRIMARY}",
            pressed_icon="settings_advanced.svg",
            pressed_color=f"{THEME_TEXT_PRIMARY}",
            icon_size=14,
            text="&Manage",
        )
        manage_excluded_btn.setFont(QFont(FONT_FAMILY, 10))
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
        excluded_dirs_info.setFont(QFont(FONT_FAMILY, 9))
        excluded_dirs_info.setStyleSheet(
            "color: rgba(192, 202, 245, 0.6); padding-left: 28px;"
        )
        scan_content_layout.addWidget(excluded_dirs_info)

        scan_section.setWidget(scan_content)
        sections_layout.addWidget(scan_section)

        # === Background & Tray Section ===
        tray_section = SettingsGroup("Background & Tray", parent=sections_container)

        tray_content = QWidget()
        tray_content_layout = QVBoxLayout(tray_content)
        tray_content_layout.setContentsMargins(8, 8, 8, 8)
        tray_content_layout.setSpacing(12)

        # Start minimized checkbox
        start_minimized_row = QWidget()
        start_minimized_layout = QHBoxLayout(start_minimized_row)
        start_minimized_layout.setContentsMargins(0, 0, 0, 0)
        start_minimized_layout.setSpacing(8)

        self.start_minimized_checkbox = QCheckBox("Start minimized to system tray")
        self.start_minimized_checkbox.setFont(QFont(FONT_FAMILY, 10))
        self.start_minimized_checkbox.setIconSize(QSize(20, 20))
        self.start_minimized_checkbox.toggled.connect(self._update_checkbox_icons)
        start_minimized_layout.addWidget(self.start_minimized_checkbox)
        start_minimized_layout.addStretch()

        tray_content_layout.addWidget(start_minimized_row)

        # Start minimized info
        start_minimized_info = QLabel(
            "When enabled, the application will start hidden in the system tray.\n"
            "Double-click the tray icon to show the window."
        )
        start_minimized_info.setFont(QFont(FONT_FAMILY, 9))
        start_minimized_info.setStyleSheet(
            "color: rgba(192, 202, 245, 0.6); padding-left: 28px;"
        )
        tray_content_layout.addWidget(start_minimized_info)

        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet(
            "background-color: rgba(192, 202, 245, 0.1); margin: 8px 0px;"
        )
        separator.setFixedHeight(1)
        tray_content_layout.addWidget(separator)

        # Autostart checkbox
        autostart_row = QWidget()
        autostart_layout = QHBoxLayout(autostart_row)
        autostart_layout.setContentsMargins(0, 0, 0, 0)
        autostart_layout.setSpacing(8)

        self.autostart_checkbox = QCheckBox("Run on Windows startup")
        self.autostart_checkbox.setFont(QFont(FONT_FAMILY, 10))
        self.autostart_checkbox.setIconSize(QSize(20, 20))
        self.autostart_checkbox.toggled.connect(self._update_checkbox_icons)
        autostart_layout.addWidget(self.autostart_checkbox)
        autostart_layout.addStretch()

        tray_content_layout.addWidget(autostart_row)

        # Autostart info
        autostart_info = QLabel(
            "Automatically launch Obsidian Forge when Windows starts.\n"
            "The application will start minimized to the system tray if that option is enabled."
        )
        autostart_info.setFont(QFont(FONT_FAMILY, 9))
        autostart_info.setStyleSheet(
            "color: rgba(192, 202, 245, 0.6); padding-left: 28px;"
        )
        tray_content_layout.addWidget(autostart_info)

        tray_section.setWidget(tray_content)
        sections_layout.addWidget(tray_section)

        # ═══════════════════════════════════════════════════════════════
        # Media Library Section
        # ═══════════════════════════════════════════════════════════════
        media_section = SettingsGroup("Media Library", parent=sections_container)

        media_content = QWidget()
        media_content_layout = QVBoxLayout(media_content)
        media_content_layout.setContentsMargins(8, 8, 8, 8)
        media_content_layout.setSpacing(12)

        # Port configuration
        port_row = QWidget()
        port_layout = QHBoxLayout(port_row)
        port_layout.setContentsMargins(0, 0, 0, 0)
        port_layout.setSpacing(8)

        port_label = QLabel("Server Port:")
        port_label.setFont(QFont(FONT_FAMILY, 10))
        port_label.setStyleSheet("color: rgba(192, 202, 245, 0.8);")
        port_label.setMinimumWidth(100)
        port_layout.addWidget(port_label)

        self.port_spinbox = QSpinBox()
        self.port_spinbox.setProperty("MainSpinBox", True)
        self.port_spinbox.setRange(5000, 9999)
        self.port_spinbox.setValue(5555)
        self.port_spinbox.setFont(QFont(FONT_FAMILY, 10))
        port_layout.addWidget(self.port_spinbox)
        port_layout.addStretch()

        media_content_layout.addWidget(port_row)

        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setStyleSheet(
            "background-color: rgba(65, 72, 104, 0.5); max-height: 1px;"
        )
        media_content_layout.addWidget(separator)

        # Media Paths label
        paths_label = QLabel("Media Folder Paths")
        paths_label.setFont(QFont(FONT_FAMILY, 10, QFont.Weight.Bold))
        paths_label.setStyleSheet("color: rgba(192, 202, 245, 0.9);")
        media_content_layout.addWidget(paths_label)

        # Path comboboxes for each media type
        books_row = self._create_media_path_row("Books:", "books")
        youtube_row = self._create_media_path_row("YouTube:", "youtube")
        movies_row = self._create_media_path_row("Movies:", "movies")
        tv_shows_row = self._create_media_path_row("TV Shows:", "tv_shows")
        documentaries_row = self._create_media_path_row("Docs:", "documentaries")

        media_content_layout.addWidget(books_row)
        media_content_layout.addWidget(youtube_row)
        media_content_layout.addWidget(movies_row)
        media_content_layout.addWidget(tv_shows_row)
        media_content_layout.addWidget(documentaries_row)

        # Info label
        media_info = QLabel(
            "Configure paths to media markdown files in your vault\n"
            "Leave as (Default) to use the standard paths"
        )
        media_info.setWordWrap(True)
        media_info.setFont(QFont(FONT_FAMILY, 9))
        media_info.setStyleSheet("color: rgba(192, 202, 245, 0.6); padding-left: 28px;")
        media_content_layout.addWidget(media_info)

        media_section.setWidget(media_content)
        sections_layout.addWidget(media_section)

        sections_layout.addStretch()

        scroll_area.setWidget(sections_container)
        main_layout.addWidget(scroll_area)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)
        button_layout.addStretch()

        validate_btn = HoverIconButtonSVG(
            normal_icon="check_outline.svg",
            normal_color=f"{COLOR_ORANGE}",
            hover_icon="check_bold.svg",
            hover_color=f"{COLOR_ORANGE}",
            pressed_icon="check_all.svg",
            pressed_color=f"{COLOR_ORANGE}",
            icon_size=14,
            text="&Validate",
        )
        validate_btn.setFont(QFont(FONT_FAMILY, 10))
        validate_btn.setProperty("ValidateButton", True)
        validate_btn.setFixedHeight(36)
        validate_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        validate_btn.setShortcut(QKeySequence("Ctrl+T"))
        validate_btn.clicked.connect(self.validate_settings)
        button_layout.addWidget(validate_btn)

        # Save button
        save_btn = HoverIconButtonSVG(
            normal_icon="save_outline.svg",
            normal_color=f"{COLOR_GREEN}",
            hover_icon="save_filled.svg",
            hover_color=f"{COLOR_GREEN}",
            pressed_icon="save_check_filled.svg",
            pressed_color=f"{COLOR_GREEN}",
            icon_size=14,
            text="&Save",
        )
        save_btn.setFont(QFont(FONT_FAMILY, 10))
        save_btn.setProperty("SaveButton", True)
        save_btn.setFixedHeight(36)
        save_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        save_btn.setDefault(True)
        save_btn.setShortcut(QKeySequence("Ctrl+Return"))
        save_btn.clicked.connect(self.save_settings)
        button_layout.addWidget(save_btn)

        # Cancel button
        cancel_btn = HoverIconButtonSVG(
            normal_icon="cancel_outline.svg",
            hover_icon="cancel_outline.svg",
            hover_color=f"{THEME_TEXT_PRIMARY}",
            pressed_icon="cancel.svg",
            pressed_color=f"{COLOR_RED}",
            icon_size=14,
            text="&Cancel",
        )
        cancel_btn.setFont(QFont(FONT_FAMILY, 10))
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
        layout.setSpacing(8)

        # Indent spacer
        indent = QLabel()
        indent.setFixedWidth(20)
        layout.addWidget(indent)

        # Label (compact)
        label = QLabel(label_text)
        label.setFont(QFont(FONT_FAMILY, 9))
        label.setStyleSheet("color: rgba(192, 202, 245, 0.7);")
        label.setMinimumWidth(60)
        label.setMaximumWidth(60)
        layout.addWidget(label)

        # ComboBox (compact)
        combo = QComboBox()
        combo.setProperty("MainComboBox", True)
        combo.setFont(QFont(FONT_FAMILY, 9))
        combo.setMinimumHeight(26)
        combo.setMaximumHeight(26)
        combo.addItem("(Default)")
        combo.setEnabled(False)

        layout.addWidget(combo, 1)

        # Store reference to combobox
        if path_type == "daily":
            self.daily_path_combo = combo
        elif path_type == "daily_journal":
            self.daily_journal_combo = combo
        elif path_type == "weekly":
            self.weekly_path_combo = combo
        elif path_type == "weekly_journal":
            self.weekly_journal_combo = combo
        elif path_type == "utils":
            self.utils_path_combo = combo
        elif path_type == "time":
            self.time_path_combo = combo

        return row

    def _create_media_path_row(self, label_text: str, media_type: str) -> QWidget:
        """Create a compact row with label and combobox for media path selection.

        Args:
            label_text: The label text to display
            media_type: The type of media (books, youtube, movies, tv_shows, documentaries)

        Returns:
            QWidget containing the row layout
        """
        row = QWidget()
        layout = QHBoxLayout(row)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # Indent spacer
        indent = QLabel()
        indent.setFixedWidth(20)
        layout.addWidget(indent)

        # Label (compact)
        label = QLabel(label_text)
        label.setFont(QFont(FONT_FAMILY, 9))
        label.setStyleSheet("color: rgba(192, 202, 245, 0.7);")
        label.setMinimumWidth(70)
        label.setMaximumWidth(70)
        layout.addWidget(label)

        # ComboBox (compact)
        combo = QComboBox()
        combo.setProperty("MainComboBox", True)
        combo.setFont(QFont(FONT_FAMILY, 9))
        combo.setMinimumHeight(26)
        combo.setMaximumHeight(26)
        combo.addItem("(Default)")
        combo.setEnabled(False)

        layout.addWidget(combo, 1)

        # Store reference to combobox
        if media_type == "books":
            self.books_combo = combo
        elif media_type == "youtube":
            self.youtube_combo = combo
        elif media_type == "movies":
            self.movies_combo = combo
        elif media_type == "tv_shows":
            self.tv_shows_combo = combo
        elif media_type == "documentaries":
            self.documentaries_combo = combo

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
        if self.config.custom_daily_journal_path:
            self._set_combobox_value(
                self.daily_journal_combo, self.config.custom_daily_journal_path
            )
        if self.config.custom_weekly_scripts_path:
            self._set_combobox_value(
                self.weekly_path_combo, self.config.custom_weekly_scripts_path
            )
        if self.config.custom_weekly_journal_path:
            self._set_combobox_value(
                self.weekly_journal_combo, self.config.custom_weekly_journal_path
            )
        if self.config.custom_utils_scripts_path:
            self._set_combobox_value(
                self.utils_path_combo, self.config.custom_utils_scripts_path
            )
        if self.config.custom_time_path:
            self._set_combobox_value(self.time_path_combo, self.config.custom_time_path)

        # Load media library settings
        self.port_spinbox.setValue(self.config.media_library_port)

        if self.config.custom_books_path:
            self._set_combobox_value(self.books_combo, self.config.custom_books_path)
        if self.config.custom_youtube_path:
            self._set_combobox_value(self.youtube_combo, self.config.custom_youtube_path)
        if self.config.custom_movies_path:
            self._set_combobox_value(self.movies_combo, self.config.custom_movies_path)
        if self.config.custom_tv_shows_path:
            self._set_combobox_value(
                self.tv_shows_combo, self.config.custom_tv_shows_path
            )
        if self.config.custom_documentaries_path:
            self._set_combobox_value(
                self.documentaries_combo, self.config.custom_documentaries_path
            )

        # Load tray settings
        self.start_minimized_checkbox.setChecked(self.config.start_minimized)
        self.autostart_checkbox.setChecked(is_autostart_enabled())

        # Initialize checkbox icons
        self._update_checkbox_icons()

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

    def _update_checkbox_icons(self) -> None:
        """Update checkbox icons based on checked state."""
        # Update Start Minimized checkbox
        if self.start_minimized_checkbox.isChecked():
            self.start_minimized_checkbox.setIcon(
                get_icon("square_check_filled.svg", color=self.color_theme["border"])
            )
        else:
            self.start_minimized_checkbox.setIcon(
                get_icon("square_check.svg", color=self.color_theme["border"])
            )

        # Update Autostart checkbox
        if self.autostart_checkbox.isChecked():
            self.autostart_checkbox.setIcon(
                get_icon("square_check_filled.svg", color=self.color_theme["border"])
            )
        else:
            self.autostart_checkbox.setIcon(
                get_icon("square_check.svg", color=self.color_theme["border"])
            )

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
        self._populate_combobox(self.daily_journal_combo, folders)
        self._populate_combobox(self.weekly_path_combo, folders)
        self._populate_combobox(self.weekly_journal_combo, folders)
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
        original_daily_journal: str = self.config.custom_daily_journal_path
        original_weekly: str = self.config.custom_weekly_scripts_path
        original_weekly_journal: str = self.config.custom_weekly_journal_path
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
        self.config.custom_daily_journal_path = (
            ""
            if self.daily_journal_combo.currentText() == "(Default)"
            else self.daily_journal_combo.currentText()
        )
        self.config.custom_weekly_scripts_path = (
            ""
            if self.weekly_path_combo.currentText() == "(Default)"
            else self.weekly_path_combo.currentText()
        )
        self.config.custom_weekly_journal_path = (
            ""
            if self.weekly_journal_combo.currentText() == "(Default)"
            else self.weekly_journal_combo.currentText()
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
        self.config.custom_daily_journal_path = original_daily_journal
        self.config.custom_weekly_scripts_path = original_weekly
        self.config.custom_weekly_journal_path = original_weekly_journal
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
        self.config.custom_daily_journal_path = (
            ""
            if self.daily_journal_combo.currentText() == "(Default)"
            else self.daily_journal_combo.currentText()
        )
        self.config.custom_weekly_scripts_path = (
            ""
            if self.weekly_path_combo.currentText() == "(Default)"
            else self.weekly_path_combo.currentText()
        )
        self.config.custom_weekly_journal_path = (
            ""
            if self.weekly_journal_combo.currentText() == "(Default)"
            else self.weekly_journal_combo.currentText()
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

        # Save media library settings
        self.config.media_library_port = self.port_spinbox.value()
        self.config.custom_books_path = (
            ""
            if self.books_combo.currentText() == "(Default)"
            else self.books_combo.currentText()
        )
        self.config.custom_youtube_path = (
            ""
            if self.youtube_combo.currentText() == "(Default)"
            else self.youtube_combo.currentText()
        )
        self.config.custom_movies_path = (
            ""
            if self.movies_combo.currentText() == "(Default)"
            else self.movies_combo.currentText()
        )
        self.config.custom_tv_shows_path = (
            ""
            if self.tv_shows_combo.currentText() == "(Default)"
            else self.tv_shows_combo.currentText()
        )
        self.config.custom_documentaries_path = (
            ""
            if self.documentaries_combo.currentText() == "(Default)"
            else self.documentaries_combo.currentText()
        )

        # Save tray settings
        self.config.start_minimized = self.start_minimized_checkbox.isChecked()

        # Handle autostart
        autostart_enabled = self.autostart_checkbox.isChecked()
        if autostart_enabled:
            if not enable_autostart():
                QMessageBox.warning(
                    self,
                    "Autostart Warning",
                    "Failed to enable autostart. Please check permissions.",
                )
        else:
            disable_autostart()

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
