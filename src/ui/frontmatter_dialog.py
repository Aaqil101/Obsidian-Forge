"""
Frontmatter editing dialog for daily and weekly notes.
Allows users to edit frontmatter fields without opening Obsidian.
"""

# ----- Built-In Modules-----
import datetime
from pathlib import Path
from typing import Optional

# ----- PySide6 Modules-----
from PySide6.QtCore import QDate, QSize, Qt, QTimer
from PySide6.QtGui import QCursor, QFont, QGuiApplication, QKeySequence
from PySide6.QtWidgets import (
    QButtonGroup,
    QCheckBox,
    QDateEdit,
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QRadioButton,
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
    calculate_daily_note_path,
    calculate_weekly_note_path,
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
    COLOR_LIGHT_BLUE,
    THEME_BORDER,
    THEME_TEXT_SECONDARY,
    HoverIconButton,
    Icons,
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
        self.current_file_path: Optional[Path] = None

        # Set title based on note type
        if note_type == "daily":
            self.setWindowTitle(f"Edit Daily Note Frontmatter - {APP_NAME}")
        elif note_type == "weekly":
            self.setWindowTitle(f"Edit Weekly Note Frontmatter - {APP_NAME}")

        self.setMinimumSize(650, 500)

        self._setup_ui()
        self._center_window()

        # Load today's note by default (daily or weekly based on note_type)
        self._on_date_changed()

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

        self.date_picker = QDateEdit()
        self.date_picker.setFont(QFont(FONT_FAMILY, 10))
        self.date_picker.setCalendarPopup(True)
        self.date_picker.setDate(QDate.currentDate())
        # Set display format based on note type
        if self.current_note_type == "daily":
            self.date_picker.setDisplayFormat("yyyy-MM-dd (dddd)")
        else:
            self.date_picker.setDisplayFormat("yyyy-MM-dd ('Week' ww)")
        self.date_picker.setMinimumHeight(32)
        self.date_picker.dateChanged.connect(self._on_date_changed)
        date_layout.addWidget(self.date_picker)

        # Status label
        self.status_label = QLabel()
        self.status_label.setFont(QFont(FONT_FAMILY, 9))
        self.status_label.setStyleSheet(f"color: {THEME_TEXT_SECONDARY};")
        date_layout.addWidget(self.status_label)

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

        cancel_btn = HoverIconButton(
            normal_icon=Icons.CANCEL_OUTLINE,
            hover_icon=Icons.CANCEL,
            text="  Cancel",
        )
        cancel_btn.setProperty("CancelButton", True)
        cancel_btn.setFont(QFont(FONT_FAMILY, 10))
        cancel_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        cancel_btn.setFixedHeight(30)
        cancel_btn.setShortcut(QKeySequence("Esc"))
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        save_btn = HoverIconButton(
            normal_icon=Icons.SAVE,
            hover_icon=Icons.CONTENT_SAVE,
            pressed_icon=Icons.CONTENT_SAVE_CHECK,
            text="  Save Changes",
        )
        save_btn.setProperty("SaveButton", True)
        save_btn.setFont(QFont(FONT_FAMILY, 10))
        save_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        save_btn.setFixedHeight(30)
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
                field_widget = self._create_field_row(
                    field_name, field_config, section_content
                )
                section_layout.addWidget(field_widget)

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
            widget.setMinimumWidth(120)
            widget.setMinimumHeight(32)
            widget.setRange(*field_config["range"])
            widget.setProperty("MainSpinBox", True)
            widget.setButtonSymbols(QSpinBox.ButtonSymbols.UpDownArrows)
            return widget

        else:  # text
            widget = QLineEdit()
            widget.setFont(QFont(FONT_FAMILY, 10))
            widget.setMinimumWidth(200)
            widget.setMinimumHeight(32)
            widget.setProperty("MainLineEdit", True)
            widget.setPlaceholderText(f"Enter {field_name.replace('_', ' ')}")
            return widget

    def _update_checkbox_icon(self, checkbox: QCheckBox, state: int) -> None:
        """Update checkbox icon based on state."""
        if state == Qt.CheckState.Checked.value:
            checkbox.setIcon(
                get_icon("square_check_filled.svg", color=COLOR_LIGHT_BLUE)
            )
        else:
            checkbox.setIcon(get_icon("square_check.svg", color=THEME_BORDER))


    def _on_date_changed(self) -> None:
        """Handle date picker change."""
        # Calculate file path
        q_date = self.date_picker.date()
        py_date = datetime.date(q_date.year(), q_date.month(), q_date.day())

        if self.current_note_type == "daily":
            self.current_file_path = calculate_daily_note_path(
                self.config.vault_path, py_date
            )
        else:
            self.current_file_path = calculate_weekly_note_path(
                self.config.vault_path, py_date
            )

        # Check if file exists
        if self.current_file_path.exists():
            self.status_label.setText(f"✓ Note exists: {self.current_file_path.name}")
            self.status_label.setStyleSheet("color: #9ece6a;")  # Green
            self._load_frontmatter()
            self.save_btn.setEnabled(True)
        else:
            self.status_label.setText(
                f"⚠️ Note not found - Create it in Obsidian first"
            )
            self.status_label.setStyleSheet("color: #e0af68;")  # Yellow
            self._clear_fields()
            self.save_btn.setEnabled(False)

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
            elif isinstance(widget, QLineEdit):
                widget.setText(str(value) if value not in [None, ""] else "")

    def _clear_fields(self) -> None:
        """Clear all field widgets."""
        for field_name, widget in self.field_widgets.items():
            if isinstance(widget, QCheckBox):
                widget.setChecked(False)
            elif isinstance(widget, QSpinBox):
                widget.setValue(widget.minimum())
            elif isinstance(widget, QLineEdit):
                widget.clear()

    def _validate_inputs(self) -> list[str]:
        """Validate all inputs and return list of errors."""
        errors = []

        for field_name, widget in self.field_widgets.items():
            if isinstance(widget, QCheckBox):
                value = widget.isChecked()
            elif isinstance(widget, QSpinBox):
                value = widget.value()
            elif isinstance(widget, QLineEdit):
                value = widget.text()
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

        # Collect values from widgets
        updates = {}
        for field_name, widget in self.field_widgets.items():
            if isinstance(widget, QCheckBox):
                updates[field_name] = widget.isChecked()
            elif isinstance(widget, QSpinBox):
                value = widget.value()
                # Only include non-zero values for optional fields
                if value != 0 or widget.minimum() != 0:
                    updates[field_name] = value
            elif isinstance(widget, QLineEdit):
                text = widget.text().strip()
                if text:  # Only include non-empty values
                    updates[field_name] = text

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
