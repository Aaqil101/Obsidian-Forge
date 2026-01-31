"""
Frontmatter editing dialog for daily and weekly notes.
Allows users to edit frontmatter fields without opening Obsidian.
"""

# ----- Built-In Modules-----
from pathlib import Path
from typing import Optional

# ----- PySide6 Modules-----
from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QCursor, QFont, QGuiApplication, QKeySequence
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDoubleSpinBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QSizePolicy,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

# ----- Core Modules-----
from src.core import APP_NAME, FONT_FAMILY, Config
from src.core.frontmatter_handler import (
    DAILY_FIELDS,
    WEEKLY_FIELDS,
    get_fields_by_section,
    parse_frontmatter,
    update_frontmatter,
    validate_field_value,
)

# ----- UI Modules-----
from src.ui.popup_window import PopupIcon, PopupWindow
from src.ui.widgets import SettingsGroup

# ----- Utils Modules-----
from src.utils import (
    COLOR_GREEN,
    COLOR_LIGHT_BLUE,
    COLOR_RED,
    THEME_BORDER,
    THEME_TEXT_PRIMARY,
    THEME_TEXT_SECONDARY,
    HoverIconButtonSVG,
    get_icon,
)


class FrontmatterDialog(QDialog):
    """Dialog for editing frontmatter in daily and weekly notes."""

    def __init__(self, config: Config, note_type: str, parent=None) -> None:
        """
        Initialize the frontmatter dialog.

        Args:
            config: Application configuration
            note_type: Type of note - must be "daily" or "weekly"
            parent: Parent widget
        """
        super().__init__(parent)
        self.config = config
        self.current_note_type = note_type
        self.field_widgets = {}  # Maps field_name -> widget
        self.field_rows = {}  # Maps field_name -> row widget for visibility control
        self.current_file_path: Optional[Path] = None

        # Set title based on note type
        if note_type == "daily":
            self.setWindowTitle(f"Edit Daily Note Frontmatter - {APP_NAME}")
        elif note_type == "weekly":
            self.setWindowTitle(f"Edit Weekly Note Frontmatter - {APP_NAME}")

        self.setMinimumSize(650, 500)

        self._setup_ui()
        self._center_window()

        # Populate dropdowns and load the most recent note
        self._populate_years()
        self._select_most_recent_note()

    def _setup_ui(self) -> None:
        """Setup the dialog UI with collapsible sections."""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(8)

        # Scroll area for content
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)

        # Container for all sections
        sections_container = QWidget()
        self.sections_layout = QVBoxLayout(sections_container)
        self.sections_layout.setContentsMargins(0, 0, 0, 0)
        self.sections_layout.setSpacing(0)

        # === Date Picker Section ===
        date_section = SettingsGroup("Date / Week", parent=sections_container)
        date_section.setSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum
        )
        date_content = QWidget()
        date_layout = QVBoxLayout(date_content)
        date_layout.setContentsMargins(8, 8, 8, 8)
        date_layout.setSpacing(8)

        # Dropdowns container
        dropdowns_layout = QHBoxLayout()
        dropdowns_layout.setSpacing(8)

        # Year dropdown (for both daily and weekly)
        year_label = QLabel("Year:")
        year_label.setFont(QFont(FONT_FAMILY, 10))
        dropdowns_layout.addWidget(year_label)

        self.year_combo = QComboBox()
        self.year_combo.setProperty("MainComboBox", True)
        self.year_combo.setFont(QFont(FONT_FAMILY, 10))
        self.year_combo.setMinimumHeight(26)
        self.year_combo.currentIndexChanged.connect(self._on_year_changed)
        dropdowns_layout.addWidget(self.year_combo)

        if self.current_note_type == "daily":
            # Month dropdown (daily only)
            month_label = QLabel("Month:")
            month_label.setFont(QFont(FONT_FAMILY, 10))
            dropdowns_layout.addWidget(month_label)

            self.month_combo = QComboBox()
            self.month_combo.setProperty("MainComboBox", True)
            self.month_combo.setFont(QFont(FONT_FAMILY, 10))
            self.month_combo.setMinimumHeight(26)
            self.month_combo.setMinimumWidth(140)
            self.month_combo.currentIndexChanged.connect(self._on_month_changed)
            dropdowns_layout.addWidget(self.month_combo)
        else:
            self.month_combo = None

        # File dropdown (for both daily and weekly)
        file_label = QLabel("File:")
        file_label.setFont(QFont(FONT_FAMILY, 10))
        dropdowns_layout.addWidget(file_label)

        self.file_combo = QComboBox()
        self.file_combo.setProperty("MainComboBox", True)
        self.file_combo.setFont(QFont(FONT_FAMILY, 10))
        self.file_combo.setMinimumHeight(26)
        self.file_combo.setMinimumWidth(140)
        self.file_combo.currentIndexChanged.connect(self._on_file_changed)
        dropdowns_layout.addWidget(self.file_combo)

        dropdowns_layout.addStretch()
        date_layout.addLayout(dropdowns_layout)

        date_section.setLayout(date_layout)
        self.sections_layout.addWidget(date_section)

        # === Dynamic Field Sections ===
        self.fields_container = QWidget()
        self.fields_layout = QVBoxLayout(self.fields_container)
        self.fields_layout.setContentsMargins(0, 0, 0, 0)
        self.fields_layout.setSpacing(0)

        self.sections_layout.addWidget(self.fields_container)

        # Build initial field sections for daily notes
        self._rebuild_field_sections()

        # Add stretch at the end
        self.sections_layout.addStretch(1)

        scroll_area.setWidget(sections_container)
        main_layout.addWidget(scroll_area)

        # === Buttons ===
        button_layout = QHBoxLayout()
        button_layout.setSpacing(8)
        button_layout.addStretch()

        cancel_btn = HoverIconButtonSVG(
            normal_icon="cancel_outline.svg",
            hover_icon="cancel_outline.svg",
            hover_color=f"{THEME_TEXT_PRIMARY}",
            pressed_icon="cancel.svg",
            pressed_color=f"{COLOR_RED}",
            icon_size=14,
            text="&Cancel",
        )
        cancel_btn.setProperty("CancelButton", True)
        cancel_btn.setFont(QFont(FONT_FAMILY, 10))
        cancel_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        cancel_btn.setFixedHeight(36)
        cancel_btn.setShortcut(QKeySequence("Esc"))
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        save_btn = HoverIconButtonSVG(
            normal_icon="save_outline.svg",
            normal_color=f"{COLOR_GREEN}",
            hover_icon="save_filled.svg",
            hover_color=f"{COLOR_GREEN}",
            pressed_icon="save_check_filled.svg",
            pressed_color=f"{COLOR_GREEN}",
            icon_size=14,
            text="&Save Changes",
        )
        save_btn.setProperty("SaveButton", True)
        save_btn.setFont(QFont(FONT_FAMILY, 10))
        save_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        save_btn.setFixedHeight(36)
        save_btn.setShortcut(QKeySequence("Ctrl+Return"))
        save_btn.clicked.connect(self._on_save)
        button_layout.addWidget(save_btn)
        self.save_btn = save_btn

        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)

    def _rebuild_field_sections(self) -> None:
        """Rebuild field sections based on current note type."""
        # Clear existing field sections
        while self.fields_layout.count():
            item = self.fields_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        self.field_widgets.clear()
        self.field_rows.clear()

        # Get field sections for current note type
        sections = get_fields_by_section(self.current_note_type)
        fields = DAILY_FIELDS if self.current_note_type == "daily" else WEEKLY_FIELDS

        # Create a section for each group
        for section_name, field_names in sections.items():
            section_group = SettingsGroup(section_name, parent=self.fields_container)
            section_group.setSizePolicy(
                QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum
            )

            section_content = QWidget()
            section_layout = QVBoxLayout(section_content)
            section_layout.setContentsMargins(8, 8, 8, 8)
            section_layout.setSpacing(12)

            for field_name in field_names:
                field_config = fields[field_name]
                field_row = self._create_field_row(
                    field_name, field_config, section_content
                )
                self.field_rows[field_name] = field_row  # Store row for visibility control
                section_layout.addWidget(field_row)

            section_group.setLayout(section_layout)
            self.fields_layout.addWidget(section_group)

    def _create_field_row(
        self, field_name: str, field_config: dict, parent: QWidget
    ) -> QWidget:
        """Create a row widget for a single field."""
        row = QWidget(parent)
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(12)

        # Label
        label = QLabel(field_name.replace("_", " ").title() + ":")
        label.setFont(QFont(FONT_FAMILY, 10))
        label.setMinimumWidth(120)
        label.setStyleSheet(f"color: {THEME_TEXT_SECONDARY};")
        row_layout.addWidget(label)

        # Input widget based on type
        widget = self._create_input_widget(field_name, field_config)
        self.field_widgets[field_name] = widget
        row_layout.addWidget(widget)

        row_layout.addStretch()

        return row

    def _create_input_widget(self, field_name: str, field_config: dict) -> QWidget:
        """Create an input widget based on field configuration."""
        field_type = field_config["type"]

        if field_type == "bool":
            widget = QCheckBox()
            widget.setFont(QFont(FONT_FAMILY, 10))
            widget.setIcon(get_icon("square_check.svg", color=THEME_BORDER))
            widget.setIconSize(QSize(20, 20))
            widget.stateChanged.connect(
                lambda state, w=widget: self._update_checkbox_icon(w, state)
            )
            return widget

        elif field_type == "int":
            widget = QSpinBox()
            widget.setFont(QFont(FONT_FAMILY, 10))
            widget.setMinimumWidth(60)
            widget.setMinimumHeight(26)
            widget.setRange(*field_config["range"])
            widget.setButtonSymbols(QSpinBox.ButtonSymbols.NoButtons)
            return widget

        elif field_type == "float":
            widget = QDoubleSpinBox()
            widget.setFont(QFont(FONT_FAMILY, 10))
            widget.setMinimumWidth(60)
            widget.setMinimumHeight(26)
            widget.setRange(*field_config["range"])
            widget.setDecimals(2)  # Allow 2 decimal places
            widget.setSingleStep(0.5)  # Increment by 0.5
            widget.setButtonSymbols(QDoubleSpinBox.ButtonSymbols.NoButtons)
            return widget

        # No other field types are currently defined
        raise ValueError(f"Unknown field type: {field_type} for field {field_name}")

    def _update_checkbox_icon(self, checkbox: QCheckBox, state: int) -> None:
        """Update checkbox icon based on state."""
        if state == Qt.CheckState.Checked.value:
            checkbox.setIcon(
                get_icon("square_check_filled.svg", color=COLOR_LIGHT_BLUE)
            )
        else:
            checkbox.setIcon(get_icon("square_check.svg", color=THEME_BORDER))

    def _populate_years(self) -> None:
        """Populate the year dropdown based on existing folders."""
        self.year_combo.blockSignals(True)
        self.year_combo.clear()

        if self.current_note_type == "daily":
            journal_path = self.config.get_daily_journal_path()
        else:
            journal_path = self.config.get_weekly_journal_path()

        if not journal_path or not journal_path.exists():
            self.year_combo.blockSignals(False)
            return

        # Get all year folders
        years = []
        for item in journal_path.iterdir():
            if item.is_dir() and item.name.isdigit():
                years.append(item.name)

        years.sort(reverse=True)  # Most recent first
        self.year_combo.addItems(years)
        self.year_combo.blockSignals(False)

        if years:
            self._on_year_changed()

    def _on_year_changed(self) -> None:
        """Handle year dropdown change."""
        if self.current_note_type == "daily":
            self._populate_months()
        else:
            self._populate_weekly_files()

    def _populate_months(self) -> None:
        """Populate the month dropdown for daily notes."""
        if not self.month_combo:
            return

        self.month_combo.blockSignals(True)
        self.month_combo.clear()

        year = self.year_combo.currentText()
        if not year:
            self.month_combo.blockSignals(False)
            return

        journal_path = self.config.get_daily_journal_path()
        if not journal_path:
            self.month_combo.blockSignals(False)
            return

        year_path = journal_path / year
        if not year_path.exists():
            self.month_combo.blockSignals(False)
            return

        # Get all month folders (format: MM-MMMM)
        months = []
        for item in year_path.iterdir():
            if item.is_dir():
                months.append(item.name)

        # Sort by month number (first 2 characters)
        months.sort(key=lambda x: x[:2], reverse=True)  # Most recent first
        self.month_combo.addItems(months)
        self.month_combo.blockSignals(False)

        if months:
            self._on_month_changed()

    def _on_month_changed(self) -> None:
        """Handle month dropdown change."""
        self._populate_daily_files()

    def _populate_daily_files(self) -> None:
        """Populate the file dropdown for daily notes."""
        self.file_combo.blockSignals(True)
        self.file_combo.clear()

        year = self.year_combo.currentText()
        month = self.month_combo.currentText() if self.month_combo else ""

        if not year or not month:
            self.file_combo.blockSignals(False)
            return

        journal_path = self.config.get_daily_journal_path()
        if not journal_path:
            self.file_combo.blockSignals(False)
            return

        month_path = journal_path / year / month
        if not month_path.exists():
            self.file_combo.blockSignals(False)
            return

        # Get all .md files
        files = []
        for item in month_path.iterdir():
            if item.is_file() and item.suffix == ".md":
                files.append(item.name)

        files.sort(reverse=True)  # Most recent first
        self.file_combo.addItems(files)
        self.file_combo.blockSignals(False)

        if files:
            self._on_file_changed()

    def _populate_weekly_files(self) -> None:
        """Populate the file dropdown for weekly notes."""
        self.file_combo.blockSignals(True)
        self.file_combo.clear()

        year = self.year_combo.currentText()
        if not year:
            self.file_combo.blockSignals(False)
            return

        journal_path = self.config.get_weekly_journal_path()
        if not journal_path:
            self.file_combo.blockSignals(False)
            return

        year_path = journal_path / year
        if not year_path.exists():
            self.file_combo.blockSignals(False)
            return

        # Get all .md files, excluding * - Data.md files
        files = []
        for item in year_path.iterdir():
            if item.is_file() and item.suffix == ".md":
                # Exclude files matching pattern *-W* - Data.md
                if not item.name.endswith(" - Data.md"):
                    files.append(item.name)

        files.sort(reverse=True)  # Most recent first
        self.file_combo.addItems(files)
        self.file_combo.blockSignals(False)

        if files:
            self._on_file_changed()

    def _on_file_changed(self) -> None:
        """Handle file dropdown change."""
        filename = self.file_combo.currentText()
        if not filename:
            self._clear_fields()
            self.save_btn.setEnabled(False)
            return

        # Build file path
        if self.current_note_type == "daily":
            year = self.year_combo.currentText()
            month = self.month_combo.currentText() if self.month_combo else ""
            journal_path = self.config.get_daily_journal_path()
            if journal_path:
                self.current_file_path = journal_path / year / month / filename
        else:
            year = self.year_combo.currentText()
            journal_path = self.config.get_weekly_journal_path()
            if journal_path:
                self.current_file_path = journal_path / year / filename

        # Load frontmatter if file exists
        if self.current_file_path and self.current_file_path.exists():
            self._load_frontmatter()
            self.save_btn.setEnabled(True)
        else:
            self._clear_fields()
            self.save_btn.setEnabled(False)

    def _select_most_recent_note(self) -> None:
        """Select the most recent note (first item in each dropdown)."""
        # The dropdowns are already populated with most recent first
        # Just ensure the first item is selected (which triggers the cascade)
        if self.year_combo.count() > 0:
            self.year_combo.setCurrentIndex(0)

    def _load_frontmatter(self) -> None:
        """Load frontmatter from the current file and populate widgets."""
        if not self.current_file_path or not self.current_file_path.exists():
            return

        frontmatter, _ = parse_frontmatter(self.current_file_path)

        # Check if frontmatter is empty
        if not frontmatter:
            popup = PopupWindow(
                message=f"Note exists but has no frontmatter:\n{self.current_file_path.name}\n\nThe note file exists but doesn't contain any frontmatter (YAML metadata).",
                title="No Frontmatter Found",
                icon=PopupIcon.WARNING,
                parent=self,
            )
            popup.exec()
            self._clear_fields()
            return

        # Update prayer field visibility based on frontmatter content
        self._update_prayer_field_visibility(frontmatter)

        # Populate widgets
        for field_name, widget in self.field_widgets.items():
            value = frontmatter.get(field_name)

            if isinstance(widget, QCheckBox):
                widget.setChecked(bool(value) if value is not None else False)
            elif isinstance(widget, QSpinBox):
                if value == "" or value is None:
                    widget.setValue(widget.minimum())
                else:
                    try:
                        widget.setValue(int(value))
                    except (ValueError, TypeError):
                        widget.setValue(widget.minimum())
            elif isinstance(widget, QDoubleSpinBox):
                if value == "" or value is None:
                    widget.setValue(widget.minimum())
                else:
                    try:
                        widget.setValue(float(value))
                    except (ValueError, TypeError):
                        widget.setValue(widget.minimum())

    def _clear_fields(self) -> None:
        """Clear all field widgets."""
        # Set default visibility (show new individual fields, hide legacy 'prayers')
        self._update_prayer_field_visibility({})

        for field_name, widget in self.field_widgets.items():
            if isinstance(widget, QCheckBox):
                widget.setChecked(False)
            elif isinstance(widget, QSpinBox):
                widget.setValue(widget.minimum())
            elif isinstance(widget, QDoubleSpinBox):
                widget.setValue(widget.minimum())

    def _update_prayer_field_visibility(self, frontmatter: dict) -> None:
        """
        Show/hide prayer fields based on what exists in the frontmatter.

        Logic:
        - If 'prayers' field exists in frontmatter, show only 'prayers' and hide individual fields
        - Otherwise, hide 'prayers' and show individual fields
        """
        has_legacy_prayers = "prayers" in frontmatter

        if self.current_note_type == "daily":
            # Individual prayer fields for daily notes
            individual_fields = ["fajr", "dhuhr", "asr", "maghrib", "isha"]
        else:  # weekly
            # Individual prayer total fields for weekly notes
            individual_fields = ["fajr_total", "dhuhr_total", "asr_total", "maghrib_total", "isha_total"]

        # Show/hide based on whether legacy 'prayers' field exists
        if "prayers" in self.field_rows:
            self.field_rows["prayers"].setVisible(has_legacy_prayers)

        for field in individual_fields:
            if field in self.field_rows:
                self.field_rows[field].setVisible(not has_legacy_prayers)

    def _validate_inputs(self) -> list[str]:
        """Validate all inputs and return list of errors."""
        errors = []

        for field_name, widget in self.field_widgets.items():
            # Skip hidden fields
            if field_name in self.field_rows and not self.field_rows[field_name].isVisible():
                continue

            if isinstance(widget, QCheckBox):
                value = widget.isChecked()
            elif isinstance(widget, QSpinBox):
                value = widget.value()
            elif isinstance(widget, QDoubleSpinBox):
                value = widget.value()
            else:
                continue

            error = validate_field_value(field_name, value, self.current_note_type)
            if error:
                errors.append(error)

        return errors

    def _on_save(self) -> None:
        """Save changes to frontmatter."""
        # Validate inputs
        errors = self._validate_inputs()
        if errors:
            popup = PopupWindow(
                message="Please fix the following errors:\n\n" + "\n".join(errors),
                title="Validation Errors",
                icon=PopupIcon.WARNING,
                parent=self,
            )
            popup.exec()
            return

        if not self.current_file_path or not self.current_file_path.exists():
            popup = PopupWindow(
                message="Note file does not exist.\n\nPlease create the note in Obsidian first using your Templater template, then use this editor to modify the frontmatter.",
                title="Note Not Found",
                icon=PopupIcon.WARNING,
                parent=self,
            )
            popup.exec()
            return

        # Collect values from widgets (only from visible fields)
        updates = {}
        for field_name, widget in self.field_widgets.items():
            # Skip hidden fields
            if field_name in self.field_rows and not self.field_rows[field_name].isVisible():
                continue

            if isinstance(widget, QCheckBox):
                updates[field_name] = widget.isChecked()
            elif isinstance(widget, QSpinBox):
                value = widget.value()
                # Only include non-zero values for optional fields
                if value != 0 or widget.minimum() != 0:
                    updates[field_name] = value
            elif isinstance(widget, QDoubleSpinBox):
                value = widget.value()
                # Only include non-zero values for optional fields
                if value != 0.0 or widget.minimum() != 0.0:
                    updates[field_name] = value

        # Update frontmatter
        success = update_frontmatter(self.current_file_path, updates)

        if success:
            popup = PopupWindow(
                message=f"Frontmatter updated successfully:\n{self.current_file_path.name}",
                title="Success",
                icon=PopupIcon.SUCCESS,
                parent=self,
            )
            popup.exec()
            self.accept()
        else:
            popup = PopupWindow(
                message=f"Failed to update frontmatter:\n{self.current_file_path.name}",
                title="Error",
                icon=PopupIcon.ERROR,
                parent=self,
            )
            popup.exec()

    def _center_window(self) -> None:
        """Center the window on the parent window."""
        if self.parent():
            parent_geometry = self.parent().frameGeometry()
            window_geometry = self.frameGeometry()
            center_point = parent_geometry.center()
            window_geometry.moveCenter(center_point)
            self.move(window_geometry.topLeft())
        else:
            # Fallback to screen center if no parent
            screen = QGuiApplication.primaryScreen().geometry()
            window_geometry = self.frameGeometry()
            center_point = screen.center()
            window_geometry.moveCenter(center_point)
            self.move(window_geometry.topLeft())
