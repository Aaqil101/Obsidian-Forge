"""
Frontmatter editing dialog for weekly notes.
Allows users to edit frontmatter fields without opening Obsidian.
"""

# ----- PySide6 Modules-----
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QComboBox,
    QDoubleSpinBox,
    QGridLayout,
    QSizePolicy,
    QSpinBox,
    QWidget,
)

# ----- Core Modules-----
from src.core import FONT_FAMILY, Config
from src.core.frontmatter_handler import WEEKLY_FIELDS

# ----- UI Modules-----
from src.ui.frontmatter.base import BaseFrontmatterDialog
from src.ui.widgets import SettingsGroup


class WeeklyFrontmatterDialog(BaseFrontmatterDialog):
    """Dialog for editing frontmatter in weekly notes."""

    def __init__(self, config: Config, parent=None) -> None:
        """
        Initialize the weekly frontmatter dialog.

        Args:
            config: Application configuration
            parent: Parent widget
        """
        super().__init__(config, "weekly", parent)
        self.setFixedSize(680, 440)

        self._setup_ui()
        self._center_window()

        # Populate dropdowns and load the most recent note
        self._populate_years()
        self._select_most_recent_note()

    def _build_date_picker_section(self, sections_container: QWidget) -> None:
        """Build the date picker section for weekly notes."""
        # === Date Picker Section ===
        date_section = SettingsGroup("Year / Week", parent=sections_container)
        date_section.setSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum
        )
        date_content = QWidget()
        date_layout = QGridLayout(date_content)
        date_layout.setContentsMargins(4, 2, 4, 2)
        date_layout.setHorizontalSpacing(16)
        date_layout.setVerticalSpacing(4)

        # Year dropdown (row 0, col 0)
        year_container = self._create_field_container("Choose The Year:", date_content)
        self.year_combo = QComboBox()
        self.year_combo.setProperty("MainComboBox", True)
        self.year_combo.setFont(QFont(FONT_FAMILY, 10))
        self.year_combo.setMinimumHeight(24)
        self.year_combo.currentIndexChanged.connect(self._on_year_changed)
        self._add_widget_to_container(year_container, self.year_combo)
        date_layout.addWidget(year_container, 0, 0)

        # File dropdown (row 0, col 2) - skip col 1 to align with other sections
        file_container = self._create_field_container("Choose The File:", date_content)
        self.file_combo = QComboBox()
        self.file_combo.setProperty("MainComboBox", True)
        self.file_combo.setFont(QFont(FONT_FAMILY, 10))
        self.file_combo.setMinimumHeight(24)
        self.file_combo.setMinimumWidth(130)
        self.file_combo.currentIndexChanged.connect(self._on_file_changed)
        self._add_widget_to_container(file_container, self.file_combo)
        date_layout.addWidget(file_container, 0, 2)

        date_section.setLayout(date_layout)
        self.sections_layout.addWidget(date_section)

    def _build_field_sections(self) -> None:
        """Build field sections for weekly notes with manually created fields."""

        # === Overview Section ===
        overview_section = SettingsGroup("Overview", parent=self.fields_container)
        overview_section.setSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum
        )
        overview_content = QWidget()
        overview_layout = QGridLayout(overview_content)
        overview_layout.setContentsMargins(4, 2, 4, 2)
        overview_layout.setHorizontalSpacing(16)
        overview_layout.setVerticalSpacing(4)

        # Weekly Overview field (row 0, col 0)
        weekly_overview_container = self._create_field_container(
            "Weekly Overview:", overview_content
        )
        self.weekly_overview_widget = QDoubleSpinBox()
        min_val, max_val = WEEKLY_FIELDS["weekly_overview"]["range"]
        self._setup_double_spinbox(
            self.weekly_overview_widget, float(min_val), float(max_val)
        )
        self._add_widget_to_container(
            weekly_overview_container, self.weekly_overview_widget
        )
        self.field_widgets["weekly_overview"] = self.weekly_overview_widget
        self.field_rows["weekly_overview"] = weekly_overview_container
        overview_layout.addWidget(weekly_overview_container, 0, 0)

        # Overall Mood field (row 0, col 2) - skip col 1 to align with Spiritual section
        overall_mood_container = self._create_field_container(
            "Overall Mood:", overview_content
        )
        self.overall_mood_widget = QDoubleSpinBox()
        min_val, max_val = WEEKLY_FIELDS["overall_mood"]["range"]
        self._setup_double_spinbox(
            self.overall_mood_widget, float(min_val), float(max_val)
        )
        self._add_widget_to_container(overall_mood_container, self.overall_mood_widget)
        self.field_widgets["overall_mood"] = self.overall_mood_widget
        self.field_rows["overall_mood"] = overall_mood_container
        overview_layout.addWidget(overall_mood_container, 0, 2)

        overview_section.setLayout(overview_layout)
        self.fields_layout.addWidget(overview_section)

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

        # Reading field (row 0, col 0)
        reading_container = self._create_field_container("Reading:", tracking_content)
        self.reading_widget = QDoubleSpinBox()
        min_val, max_val = WEEKLY_FIELDS["reading"]["range"]
        self._setup_double_spinbox(self.reading_widget, float(min_val), float(max_val))
        self._add_widget_to_container(reading_container, self.reading_widget)
        self.field_widgets["reading"] = self.reading_widget
        self.field_rows["reading"] = reading_container
        tracking_layout.addWidget(reading_container, 0, 0)

        # Learn Blender field (row 0, col 2) - skip col 1 to align with Spiritual section
        learn_blender_container = self._create_field_container(
            "Learn Blender:", tracking_content
        )
        self.learn_blender_widget = QDoubleSpinBox()
        min_val, max_val = WEEKLY_FIELDS["learn_blender"]["range"]
        self._setup_double_spinbox(
            self.learn_blender_widget, float(min_val), float(max_val)
        )
        self._add_widget_to_container(
            learn_blender_container, self.learn_blender_widget
        )
        self.field_widgets["learn_blender"] = self.learn_blender_widget
        self.field_rows["learn_blender"] = learn_blender_container
        tracking_layout.addWidget(learn_blender_container, 0, 2)

        # Learn Python field (row 1, col 0)
        learn_python_container = self._create_field_container(
            "Learn Python:", tracking_content
        )
        self.learn_python_widget = QDoubleSpinBox()
        min_val, max_val = WEEKLY_FIELDS["learn_python"]["range"]
        self._setup_double_spinbox(
            self.learn_python_widget, float(min_val), float(max_val)
        )
        self._add_widget_to_container(learn_python_container, self.learn_python_widget)
        self.field_widgets["learn_python"] = self.learn_python_widget
        self.field_rows["learn_python"] = learn_python_container
        tracking_layout.addWidget(learn_python_container, 1, 0)

        # Learn AHK field (row 1, col 2) - skip col 1 to align with Spiritual section
        learn_ahk_container = self._create_field_container(
            "Learn Ahk:", tracking_content
        )
        self.learn_ahk_widget = QDoubleSpinBox()
        min_val, max_val = WEEKLY_FIELDS["learn_ahk"]["range"]
        self._setup_double_spinbox(
            self.learn_ahk_widget, float(min_val), float(max_val)
        )
        self._add_widget_to_container(learn_ahk_container, self.learn_ahk_widget)
        self.field_widgets["learn_ahk"] = self.learn_ahk_widget
        self.field_rows["learn_ahk"] = learn_ahk_container
        tracking_layout.addWidget(learn_ahk_container, 1, 2)

        tracking_section.setLayout(tracking_layout)
        self.fields_layout.addWidget(tracking_section)

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
        min_val, max_val = WEEKLY_FIELDS["MAD"]["range"]
        self._setup_spinbox(self.mad_widget, min_val, max_val)
        self._add_widget_to_container(mad_container, self.mad_widget)
        self.field_widgets["MAD"] = self.mad_widget
        self.field_rows["MAD"] = mad_container
        metrics_layout.addWidget(mad_container, 0, 0)

        # PAD field (row 0, col 2) - skip col 1 to align with Spiritual section
        pad_container = self._create_field_container("P Per Day:", metrics_content)
        self.pad_widget = QSpinBox()
        min_val, max_val = WEEKLY_FIELDS["PAD"]["range"]
        self._setup_spinbox(self.pad_widget, min_val, max_val)
        self._add_widget_to_container(pad_container, self.pad_widget)
        self.field_widgets["PAD"] = self.pad_widget
        self.field_rows["PAD"] = pad_container
        metrics_layout.addWidget(pad_container, 0, 2)

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

        # Fajr Sunnah Total field (row 0, col 0)
        fajr_sunnah_total_container = self._create_field_container(
            "Fajr Sunnah Total:", spiritual_content
        )
        self.fajr_sunnah_total_widget = QSpinBox()
        min_val, max_val = WEEKLY_FIELDS["fajr_sunnah_total"]["range"]
        self._setup_spinbox(self.fajr_sunnah_total_widget, min_val, max_val)
        self._add_widget_to_container(
            fajr_sunnah_total_container, self.fajr_sunnah_total_widget
        )
        self.field_widgets["fajr_sunnah_total"] = self.fajr_sunnah_total_widget
        self.field_rows["fajr_sunnah_total"] = fajr_sunnah_total_container
        spiritual_layout.addWidget(fajr_sunnah_total_container, 0, 0)

        # Fajr Total field (row 0, col 1)
        fajr_total_container = self._create_field_container(
            "Fajr Total:", spiritual_content
        )
        self.fajr_total_widget = QSpinBox()
        min_val, max_val = WEEKLY_FIELDS["fajr_total"]["range"]
        self._setup_spinbox(self.fajr_total_widget, min_val, max_val)
        self._add_widget_to_container(fajr_total_container, self.fajr_total_widget)
        self.field_widgets["fajr_total"] = self.fajr_total_widget
        self.field_rows["fajr_total"] = fajr_total_container
        spiritual_layout.addWidget(fajr_total_container, 0, 1)

        # Dhuhr Total field (row 0, col 2)
        dhuhr_total_container = self._create_field_container(
            "Dhuhr Total:", spiritual_content
        )
        self.dhuhr_total_widget = QSpinBox()
        min_val, max_val = WEEKLY_FIELDS["dhuhr_total"]["range"]
        self._setup_spinbox(self.dhuhr_total_widget, min_val, max_val)
        self._add_widget_to_container(dhuhr_total_container, self.dhuhr_total_widget)
        self.field_widgets["dhuhr_total"] = self.dhuhr_total_widget
        self.field_rows["dhuhr_total"] = dhuhr_total_container
        spiritual_layout.addWidget(dhuhr_total_container, 0, 2)

        # Asr Total field (row 1, col 0)
        asr_total_container = self._create_field_container(
            "Asr Total:", spiritual_content
        )
        self.asr_total_widget = QSpinBox()
        min_val, max_val = WEEKLY_FIELDS["asr_total"]["range"]
        self._setup_spinbox(self.asr_total_widget, min_val, max_val)
        self._add_widget_to_container(asr_total_container, self.asr_total_widget)
        self.field_widgets["asr_total"] = self.asr_total_widget
        self.field_rows["asr_total"] = asr_total_container
        spiritual_layout.addWidget(asr_total_container, 1, 0)

        # Maghrib Total field (row 1, col 1)
        maghrib_total_container = self._create_field_container(
            "Maghrib Total:", spiritual_content
        )
        self.maghrib_total_widget = QSpinBox()
        min_val, max_val = WEEKLY_FIELDS["maghrib_total"]["range"]
        self._setup_spinbox(self.maghrib_total_widget, min_val, max_val)
        self._add_widget_to_container(
            maghrib_total_container, self.maghrib_total_widget
        )
        self.field_widgets["maghrib_total"] = self.maghrib_total_widget
        self.field_rows["maghrib_total"] = maghrib_total_container
        spiritual_layout.addWidget(maghrib_total_container, 1, 1)

        # Isha Total field (row 1, col 2)
        isha_total_container = self._create_field_container(
            "Isha Total:", spiritual_content
        )
        self.isha_total_widget = QSpinBox()
        min_val, max_val = WEEKLY_FIELDS["isha_total"]["range"]
        self._setup_spinbox(self.isha_total_widget, min_val, max_val)
        self._add_widget_to_container(isha_total_container, self.isha_total_widget)
        self.field_widgets["isha_total"] = self.isha_total_widget
        self.field_rows["isha_total"] = isha_total_container
        spiritual_layout.addWidget(isha_total_container, 1, 2)

        # Prayers (Legacy) field (row 2, col 0)
        prayers_container = self._create_field_container("Prayers:", spiritual_content)
        self.prayers_widget = QSpinBox()
        min_val, max_val = WEEKLY_FIELDS["prayers"]["range"]
        self._setup_spinbox(self.prayers_widget, min_val, max_val)
        self._add_widget_to_container(prayers_container, self.prayers_widget)
        self.field_widgets["prayers"] = self.prayers_widget
        self.field_rows["prayers"] = prayers_container
        spiritual_layout.addWidget(prayers_container, 2, 0)

        spiritual_section.setLayout(spiritual_layout)
        self.fields_layout.addWidget(spiritual_section)

    def _populate_years(self) -> None:
        """Populate the year dropdown based on existing folders."""
        self.year_combo.blockSignals(True)
        self.year_combo.clear()

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
        self._populate_weekly_files()

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

    def _get_individual_prayer_fields(self) -> list[str]:
        """
        Return list of individual prayer field names for weekly notes.

        Returns:
            List of prayer total field names
        """
        return [
            "fajr_total",
            "dhuhr_total",
            "asr_total",
            "maghrib_total",
            "isha_total",
        ]

    def _get_longest_label(self) -> str:
        """
        Return the longest label text for weekly notes.

        Returns:
            The longest label string for proper alignment
        """
        return "Fajr Sunnah Total:"
