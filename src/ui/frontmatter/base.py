"""
Base class for frontmatter editing dialogs.
Provides shared functionality for daily and weekly note frontmatter editors.
"""

# ----- Built-In Modules-----
from abc import abstractmethod
from pathlib import Path
from typing import Optional

# ----- PySide6 Modules-----
from PySide6.QtCore import Qt
from PySide6.QtGui import QCursor, QFont, QFontMetrics, QGuiApplication, QKeySequence
from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QDoubleSpinBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

# ----- Core Modules-----
from src.core import APP_NAME, FONT_FAMILY, Config
from src.core.frontmatter_handler import (
    parse_frontmatter,
    update_frontmatter,
    validate_field_value,
)

# ----- UI Modules-----
from src.ui.popup_window import PopupIcon, PopupWindow

# ----- Utils Modules-----
from src.utils import COLOR_GREEN, COLOR_RED, THEME_TEXT_PRIMARY, HoverIconButtonSVG


class BaseFrontmatterDialog(QDialog):
    """Base dialog for editing frontmatter in notes."""

    def __init__(self, config: Config, note_type: str, parent=None) -> None:
        """
        Initialize the base frontmatter dialog.

        Args:
            config: Application configuration
            note_type: Type of note ("daily" or "weekly")
            parent: Parent widget
        """
        super().__init__(parent)
        self.config = config
        self.note_type = note_type
        self.field_widgets = {}  # Maps field_name -> widget
        self.field_rows = {}  # Maps field_name -> row widget for visibility control
        self.current_file_path: Optional[Path] = None

        self.setWindowTitle(f"Edit {note_type.title()} Note Frontmatter - {APP_NAME}")

    def _setup_ui(self) -> None:
        """Setup the dialog UI with collapsible sections."""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(4)

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

        # === Date Picker Section (implemented by subclass) ===
        self._build_date_picker_section(sections_container)

        # === Dynamic Field Sections ===
        self.fields_container = QWidget()
        self.fields_layout = QVBoxLayout(self.fields_container)
        self.fields_layout.setContentsMargins(0, 0, 0, 0)
        self.fields_layout.setSpacing(0)

        self.sections_layout.addWidget(self.fields_container)

        # Build field sections (implemented by subclass)
        self._build_field_sections()

        # Add stretch at the end
        self.sections_layout.addStretch(1)

        scroll_area.setWidget(sections_container)
        main_layout.addWidget(scroll_area)

        # === Buttons ===
        button_layout = QHBoxLayout()
        button_layout.setSpacing(6)
        button_layout.addStretch()

        cancel_btn = HoverIconButtonSVG(
            normal_icon="cancel_outline.svg",
            hover_icon="cancel_outline.svg",
            hover_color=f"{THEME_TEXT_PRIMARY}",
            pressed_icon="cancel.svg",
            pressed_color=f"{COLOR_RED}",
            icon_size=16,
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
            icon_size=16,
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

    def _create_field_container(self, label_text: str, parent: QWidget) -> QWidget:
        """Create a field container with label."""
        container = QWidget(parent)
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        # Label
        label = QLabel(label_text)
        label.setFont(QFont(FONT_FAMILY, 10))

        # Calculate the width needed for the longest label
        font_metrics = QFontMetrics(label.font())
        # Get the longest label from the subclass
        longest_label = self._get_longest_label()
        label_width: int = font_metrics.horizontalAdvance(longest_label)
        label.setMinimumWidth(label_width)

        layout.addWidget(label)

        return container

    def _add_widget_to_container(self, container: QWidget, widget: QWidget) -> None:
        """Add widget to container and add stretch."""
        layout = container.layout()
        layout.addWidget(widget)
        layout.addStretch()

    def _setup_spinbox(self, spinbox: QSpinBox, min_val: int, max_val: int) -> None:
        """Setup a spinbox with common properties."""
        spinbox.setFont(QFont(FONT_FAMILY, 10))
        spinbox.setMinimumWidth(50)
        spinbox.setMinimumHeight(24)
        spinbox.setRange(min_val, max_val)
        spinbox.setButtonSymbols(QSpinBox.ButtonSymbols.NoButtons)

    def _setup_double_spinbox(
        self, spinbox: QDoubleSpinBox, min_val: float, max_val: float
    ) -> None:
        """Setup a double spinbox with common properties."""
        spinbox.setFont(QFont(FONT_FAMILY, 10))
        spinbox.setMinimumWidth(50)
        spinbox.setMinimumHeight(24)
        spinbox.setRange(min_val, max_val)
        spinbox.setDecimals(2)  # Allow 2 decimal places
        spinbox.setSingleStep(0.5)  # Increment by 0.5
        spinbox.setButtonSymbols(QDoubleSpinBox.ButtonSymbols.NoButtons)

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

        # Get individual prayer fields from subclass
        individual_fields: list[str] = self._get_individual_prayer_fields()

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
            if (
                field_name in self.field_rows
                and not self.field_rows[field_name].isVisible()
            ):
                continue

            if isinstance(widget, QCheckBox):
                value: bool = widget.isChecked()
            elif isinstance(widget, QSpinBox):
                value = widget.value()
            elif isinstance(widget, QDoubleSpinBox):
                value = widget.value()
            else:
                continue

            error = validate_field_value(field_name, value, self.note_type)
            if error:
                errors.append(error)

        return errors

    def _on_save(self) -> None:
        """Save changes to frontmatter."""
        # Validate inputs
        errors: list[str] = self._validate_inputs()
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
            if (
                field_name in self.field_rows
                and not self.field_rows[field_name].isVisible()
            ):
                continue

            if isinstance(widget, QCheckBox):
                updates[field_name] = widget.isChecked()
            elif isinstance(widget, QSpinBox):
                updates[field_name] = widget.value()
            elif isinstance(widget, QDoubleSpinBox):
                value = widget.value()
                # Save zero as integer "0" instead of "0.00"
                updates[field_name] = 0 if value == 0 else value

        # Update frontmatter
        success: bool = update_frontmatter(self.current_file_path, updates)

        if success:
            popup = PopupWindow(
                message=f"Frontmatter updated successfully:\n{self.current_file_path.name}",
                title="Success",
                icon=PopupIcon.SUCCESS,
                parent=self,
                auto_close_ms=1000,
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

    # === Abstract Methods (to be implemented by subclasses) ===
    @abstractmethod
    def _build_date_picker_section(self, sections_container: QWidget) -> None:
        """
        Build the date/file picker section for this note type.

        Args:
            sections_container: The container widget to add the section to
        """
        pass

    @abstractmethod
    def _build_field_sections(self) -> None:
        """Build field sections for this note type."""
        pass

    @abstractmethod
    def _get_individual_prayer_fields(self) -> list[str]:
        """
        Return list of individual prayer field names for this note type.

        Returns:
            List of field names for individual prayers
        """
        pass

    @abstractmethod
    def _select_most_recent_note(self) -> None:
        """Select the most recent note in the dropdowns."""
        pass

    @abstractmethod
    def _get_longest_label(self) -> str:
        """
        Return the longest label text for this note type.
        Used to calculate minimum label width for proper alignment.

        Returns:
            The longest label string (e.g., "Learn Blender:" for daily, "Fajr Sunnah Total:" for weekly)
        """
        pass
