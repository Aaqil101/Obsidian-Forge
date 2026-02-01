"""
Frontmatter editing dialog for daily notes.
Allows users to edit frontmatter fields without opening Obsidian.
"""

# ----- PySide6 Modules-----
from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QSizePolicy,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

# ----- Core Modules-----
from src.core import FONT_FAMILY, Config
from src.core.frontmatter_handler import DAILY_FIELDS

# ----- UI Modules-----
from src.ui.frontmatter.base import BaseFrontmatterDialog
from src.ui.widgets import SettingsGroup

# ----- Utils Modules-----
from src.utils import COLOR_LIGHT_BLUE, THEME_BORDER, get_icon


class DailyFrontmatterDialog(BaseFrontmatterDialog):
    """Dialog for editing frontmatter in daily notes."""

    def __init__(self, config: Config, parent=None) -> None:
        """
        Initialize the daily frontmatter dialog.

        Args:
            config: Application configuration
            parent: Parent widget
        """
        super().__init__(config, "daily", parent)
        self.setFixedSize(520, 440)

        self._setup_ui()
        self._center_window()

        # Populate dropdowns and load the most recent note
        self._populate_years()
        self._select_most_recent_note()

    def _build_date_picker_section(self, sections_container: QWidget) -> None:
        """Build the date picker section for daily notes."""
        # === Date Picker Section ===
        date_section = SettingsGroup("Year / Month / Day", parent=sections_container)
        date_section.setSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum
        )
        date_content = QWidget()
        date_layout = QVBoxLayout(date_content)
        date_layout.setContentsMargins(4, 2, 4, 2)
        date_layout.setSpacing(4)

        # Dropdowns container
        dropdowns_layout = QHBoxLayout()
        dropdowns_layout.setSpacing(6)

        # Year dropdown
        year_label = QLabel("Year:")
        year_label.setFont(QFont(FONT_FAMILY, 10))
        dropdowns_layout.addWidget(year_label)

        self.year_combo = QComboBox()
        self.year_combo.setProperty("MainComboBox", True)
        self.year_combo.setFont(QFont(FONT_FAMILY, 10))
        self.year_combo.setMinimumHeight(24)
        self.year_combo.currentIndexChanged.connect(self._on_year_changed)
        dropdowns_layout.addWidget(self.year_combo)

        # Month dropdown
        month_label = QLabel("Month:")
        month_label.setFont(QFont(FONT_FAMILY, 10))
        dropdowns_layout.addWidget(month_label)

        self.month_combo = QComboBox()
        self.month_combo.setProperty("MainComboBox", True)
        self.month_combo.setFont(QFont(FONT_FAMILY, 10))
        self.month_combo.setMinimumHeight(24)
        self.month_combo.setMinimumWidth(130)
        self.month_combo.currentIndexChanged.connect(self._on_month_changed)
        dropdowns_layout.addWidget(self.month_combo)

        # File dropdown
        file_label = QLabel("File:")
        file_label.setFont(QFont(FONT_FAMILY, 10))
        dropdowns_layout.addWidget(file_label)

        self.file_combo = QComboBox()
        self.file_combo.setProperty("MainComboBox", True)
        self.file_combo.setFont(QFont(FONT_FAMILY, 10))
        self.file_combo.setMinimumHeight(24)
        self.file_combo.setMinimumWidth(140)
        self.file_combo.currentIndexChanged.connect(self._on_file_changed)
        dropdowns_layout.addWidget(self.file_combo)

        dropdowns_layout.addStretch()
        date_layout.addLayout(dropdowns_layout)

        date_section.setLayout(date_layout)
        self.sections_layout.addWidget(date_section)

    def _build_field_sections(self) -> None:
        """Build field sections for daily notes with manually created fields."""

        # === Tracking Section ===
        tracking_section = SettingsGroup("Tracking", parent=self.fields_container)
        tracking_section.setSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum
        )
        tracking_content = QWidget()
        tracking_layout = QGridLayout(tracking_content)
        tracking_layout.setContentsMargins(4, 2, 4, 2)
        tracking_layout.setHorizontalSpacing(16)
        tracking_layout.setVerticalSpacing(4)

        # Book field (row 0, col 0)
        book_container = self._create_field_container("Book:", tracking_content)
        self.book_widget = QDoubleSpinBox()
        min_val, max_val = DAILY_FIELDS["book"]["range"]
        self._setup_double_spinbox(self.book_widget, float(min_val), float(max_val))
        self._add_widget_to_container(book_container, self.book_widget)
        self.field_widgets["book"] = self.book_widget
        self.field_rows["book"] = book_container
        tracking_layout.addWidget(book_container, 0, 0)

        # Learn Blender field (row 0, col 1)
        learn_blender_container = self._create_field_container(
            "Learn Blender:", tracking_content
        )
        self.learn_blender_widget = QDoubleSpinBox()
        min_val, max_val = DAILY_FIELDS["learn_blender"]["range"]
        self._setup_double_spinbox(
            self.learn_blender_widget, float(min_val), float(max_val)
        )
        self._add_widget_to_container(learn_blender_container, self.learn_blender_widget)
        self.field_widgets["learn_blender"] = self.learn_blender_widget
        self.field_rows["learn_blender"] = learn_blender_container
        tracking_layout.addWidget(learn_blender_container, 0, 1)

        # Learn Python field (row 1, col 0)
        learn_python_container = self._create_field_container(
            "Learn Python:", tracking_content
        )
        self.learn_python_widget = QDoubleSpinBox()
        min_val, max_val = DAILY_FIELDS["learn_python"]["range"]
        self._setup_double_spinbox(
            self.learn_python_widget, float(min_val), float(max_val)
        )
        self._add_widget_to_container(learn_python_container, self.learn_python_widget)
        self.field_widgets["learn_python"] = self.learn_python_widget
        self.field_rows["learn_python"] = learn_python_container
        tracking_layout.addWidget(learn_python_container, 1, 0)

        # Learn AHK field (row 1, col 1)
        learn_ahk_container = self._create_field_container("Learn Ahk:", tracking_content)
        self.learn_ahk_widget = QDoubleSpinBox()
        min_val, max_val = DAILY_FIELDS["learn_ahk"]["range"]
        self._setup_double_spinbox(self.learn_ahk_widget, float(min_val), float(max_val))
        self._add_widget_to_container(learn_ahk_container, self.learn_ahk_widget)
        self.field_widgets["learn_ahk"] = self.learn_ahk_widget
        self.field_rows["learn_ahk"] = learn_ahk_container
        tracking_layout.addWidget(learn_ahk_container, 1, 1)

        tracking_section.setLayout(tracking_layout)
        self.fields_layout.addWidget(tracking_section)

        # === Mood Section ===
        mood_section = SettingsGroup("Mood", parent=self.fields_container)
        mood_section.setSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum
        )
        mood_content = QWidget()
        mood_layout = QGridLayout(mood_content)
        mood_layout.setContentsMargins(4, 2, 4, 2)
        mood_layout.setHorizontalSpacing(16)
        mood_layout.setVerticalSpacing(4)

        # Morning Mood field (row 0, col 0)
        morning_mood_container = self._create_field_container("Morning Mood:", mood_content)
        self.morning_mood_widget = QSpinBox()
        min_val, max_val = DAILY_FIELDS["morning_mood"]["range"]
        self._setup_spinbox(self.morning_mood_widget, min_val, max_val)
        self._add_widget_to_container(morning_mood_container, self.morning_mood_widget)
        self.field_widgets["morning_mood"] = self.morning_mood_widget
        self.field_rows["morning_mood"] = morning_mood_container
        mood_layout.addWidget(morning_mood_container, 0, 0)

        # Evening Mood field (row 0, col 1)
        evening_mood_container = self._create_field_container("Evening Mood:", mood_content)
        self.evening_mood_widget = QSpinBox()
        min_val, max_val = DAILY_FIELDS["evening_mood"]["range"]
        self._setup_spinbox(self.evening_mood_widget, min_val, max_val)
        self._add_widget_to_container(evening_mood_container, self.evening_mood_widget)
        self.field_widgets["evening_mood"] = self.evening_mood_widget
        self.field_rows["evening_mood"] = evening_mood_container
        mood_layout.addWidget(evening_mood_container, 0, 1)

        mood_section.setLayout(mood_layout)
        self.fields_layout.addWidget(mood_section)

        # === Metrics Section ===
        metrics_section = SettingsGroup("Metrics", parent=self.fields_container)
        metrics_section.setSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum
        )
        metrics_content = QWidget()
        metrics_layout = QGridLayout(metrics_content)
        metrics_layout.setContentsMargins(4, 2, 4, 2)
        metrics_layout.setHorizontalSpacing(16)
        metrics_layout.setVerticalSpacing(4)

        # MAD field (row 0, col 0)
        mad_container = self._create_field_container("M Per Day:", metrics_content)
        self.mad_widget = QSpinBox()
        min_val, max_val = DAILY_FIELDS["MAD"]["range"]
        self._setup_spinbox(self.mad_widget, min_val, max_val)
        self._add_widget_to_container(mad_container, self.mad_widget)
        self.field_widgets["MAD"] = self.mad_widget
        self.field_rows["MAD"] = mad_container
        metrics_layout.addWidget(mad_container, 0, 0)

        # PAD field (row 0, col 1)
        pad_container = self._create_field_container("P Per Day:", metrics_content)
        self.pad_widget = QSpinBox()
        min_val, max_val = DAILY_FIELDS["PAD"]["range"]
        self._setup_spinbox(self.pad_widget, min_val, max_val)
        self._add_widget_to_container(pad_container, self.pad_widget)
        self.field_widgets["PAD"] = self.pad_widget
        self.field_rows["PAD"] = pad_container
        metrics_layout.addWidget(pad_container, 0, 1)

        metrics_section.setLayout(metrics_layout)
        self.fields_layout.addWidget(metrics_section)

        # === Spiritual Section ===
        spiritual_section = SettingsGroup("Spiritual", parent=self.fields_container)
        spiritual_section.setSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum
        )
        spiritual_content = QWidget()
        spiritual_layout = QGridLayout(spiritual_content)
        spiritual_layout.setContentsMargins(4, 2, 4, 2)
        spiritual_layout.setHorizontalSpacing(16)
        spiritual_layout.setVerticalSpacing(4)

        # Fajr Sunnah field (row 0, col 0)
        fajr_sunnah_container = self._create_field_container(
            "Fajr Sunnah:", spiritual_content
        )
        self.fajr_sunnah_widget = QCheckBox()
        self.fajr_sunnah_widget.setFont(QFont(FONT_FAMILY, 10))
        self.fajr_sunnah_widget.setMinimumSize(24, 24)
        self.fajr_sunnah_widget.setIcon(get_icon("square_check.svg", color=THEME_BORDER))
        self.fajr_sunnah_widget.setIconSize(QSize(20, 20))
        self.fajr_sunnah_widget.stateChanged.connect(
            lambda state, w=self.fajr_sunnah_widget: self._update_checkbox_icon(w, state)
        )
        self._add_widget_to_container(fajr_sunnah_container, self.fajr_sunnah_widget)
        self.field_widgets["fajr_sunnah"] = self.fajr_sunnah_widget
        self.field_rows["fajr_sunnah"] = fajr_sunnah_container
        spiritual_layout.addWidget(fajr_sunnah_container, 0, 0)

        # Fajr field (row 0, col 1)
        fajr_container = self._create_field_container("Fajr:", spiritual_content)
        self.fajr_widget = QCheckBox()
        self.fajr_widget.setFont(QFont(FONT_FAMILY, 10))
        self.fajr_widget.setMinimumSize(24, 24)
        self.fajr_widget.setIcon(get_icon("square_check.svg", color=THEME_BORDER))
        self.fajr_widget.setIconSize(QSize(20, 20))
        self.fajr_widget.stateChanged.connect(
            lambda state, w=self.fajr_widget: self._update_checkbox_icon(w, state)
        )
        self._add_widget_to_container(fajr_container, self.fajr_widget)
        self.field_widgets["fajr"] = self.fajr_widget
        self.field_rows["fajr"] = fajr_container
        spiritual_layout.addWidget(fajr_container, 0, 1)

        # Dhuhr field (row 0, col 2)
        dhuhr_container = self._create_field_container("Dhuhr:", spiritual_content)
        self.dhuhr_widget = QCheckBox()
        self.dhuhr_widget.setFont(QFont(FONT_FAMILY, 10))
        self.dhuhr_widget.setMinimumSize(24, 24)
        self.dhuhr_widget.setIcon(get_icon("square_check.svg", color=THEME_BORDER))
        self.dhuhr_widget.setIconSize(QSize(20, 20))
        self.dhuhr_widget.stateChanged.connect(
            lambda state, w=self.dhuhr_widget: self._update_checkbox_icon(w, state)
        )
        self._add_widget_to_container(dhuhr_container, self.dhuhr_widget)
        self.field_widgets["dhuhr"] = self.dhuhr_widget
        self.field_rows["dhuhr"] = dhuhr_container
        spiritual_layout.addWidget(dhuhr_container, 0, 2)

        # Asr field (row 1, col 0)
        asr_container = self._create_field_container("Asr:", spiritual_content)
        self.asr_widget = QCheckBox()
        self.asr_widget.setFont(QFont(FONT_FAMILY, 10))
        self.asr_widget.setMinimumSize(24, 24)
        self.asr_widget.setIcon(get_icon("square_check.svg", color=THEME_BORDER))
        self.asr_widget.setIconSize(QSize(20, 20))
        self.asr_widget.stateChanged.connect(
            lambda state, w=self.asr_widget: self._update_checkbox_icon(w, state)
        )
        self._add_widget_to_container(asr_container, self.asr_widget)
        self.field_widgets["asr"] = self.asr_widget
        self.field_rows["asr"] = asr_container
        spiritual_layout.addWidget(asr_container, 1, 0)

        # Maghrib field (row 1, col 1)
        maghrib_container = self._create_field_container("Maghrib:", spiritual_content)
        self.maghrib_widget = QCheckBox()
        self.maghrib_widget.setFont(QFont(FONT_FAMILY, 10))
        self.maghrib_widget.setMinimumSize(24, 24)
        self.maghrib_widget.setIcon(get_icon("square_check.svg", color=THEME_BORDER))
        self.maghrib_widget.setIconSize(QSize(20, 20))
        self.maghrib_widget.stateChanged.connect(
            lambda state, w=self.maghrib_widget: self._update_checkbox_icon(w, state)
        )
        self._add_widget_to_container(maghrib_container, self.maghrib_widget)
        self.field_widgets["maghrib"] = self.maghrib_widget
        self.field_rows["maghrib"] = maghrib_container
        spiritual_layout.addWidget(maghrib_container, 1, 1)

        # Isha field (row 1, col 2)
        isha_container = self._create_field_container("Isha:", spiritual_content)
        self.isha_widget = QCheckBox()
        self.isha_widget.setFont(QFont(FONT_FAMILY, 10))
        self.isha_widget.setMinimumSize(24, 24)
        self.isha_widget.setIcon(get_icon("square_check.svg", color=THEME_BORDER))
        self.isha_widget.setIconSize(QSize(20, 20))
        self.isha_widget.stateChanged.connect(
            lambda state, w=self.isha_widget: self._update_checkbox_icon(w, state)
        )
        self._add_widget_to_container(isha_container, self.isha_widget)
        self.field_widgets["isha"] = self.isha_widget
        self.field_rows["isha"] = isha_container
        spiritual_layout.addWidget(isha_container, 1, 2)

        # Prayers (Legacy) field (row 2, col 0)
        prayers_container = self._create_field_container("Prayers:", spiritual_content)
        self.prayers_widget = QSpinBox()
        min_val, max_val = DAILY_FIELDS["prayers"]["range"]
        self._setup_spinbox(self.prayers_widget, min_val, max_val)
        self._add_widget_to_container(prayers_container, self.prayers_widget)
        self.field_widgets["prayers"] = self.prayers_widget
        self.field_rows["prayers"] = prayers_container
        spiritual_layout.addWidget(prayers_container, 2, 0)

        spiritual_section.setLayout(spiritual_layout)
        self.fields_layout.addWidget(spiritual_section)

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

        journal_path = self.config.get_daily_journal_path()

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
        self._populate_months()

    def _populate_months(self) -> None:
        """Populate the month dropdown for daily notes."""
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

        year: str = self.year_combo.currentText()
        month: str = self.month_combo.currentText()

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

    def _on_file_changed(self) -> None:
        """Handle file dropdown change."""
        filename: str = self.file_combo.currentText()
        if not filename:
            self._clear_fields()
            self.save_btn.setEnabled(False)
            return

        # Build file path
        year: str = self.year_combo.currentText()
        month: str = self.month_combo.currentText()
        journal_path = self.config.get_daily_journal_path()
        if journal_path:
            self.current_file_path = journal_path / year / month / filename

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

    def _get_individual_prayer_fields(self) -> list[str]:
        """
        Return list of individual prayer field names for daily notes.

        Returns:
            List of prayer field names
        """
        return ["fajr", "dhuhr", "asr", "maghrib", "isha"]

    def _get_longest_label(self) -> str:
        """
        Return the longest label text for daily notes.

        Returns:
            The longest label string for proper alignment
        """
        return "Learn Blender:"
