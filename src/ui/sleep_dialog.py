"""
Sleep input dialog for collecting all sleep-related inputs upfront.
This dialog pre-collects all the data needed by the add-daily-sleep.js script.
"""

# ----- Built-In Modules-----
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

# ----- PySide6 Modules-----
from PySide6.QtCore import QSize, Qt, QTimer
from PySide6.QtGui import QCursor, QFont, QGuiApplication, QKeySequence
from PySide6.QtWidgets import (
    QButtonGroup,
    QComboBox,
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QRadioButton,
    QScrollArea,
    QSizePolicy,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

# ----- Core Modules-----
from src.core import APP_NAME, FONT_FAMILY, Config

# ----- UI Modules-----
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


@dataclass
class TimeEntry:
    """Represents a sleep/wake time entry from Time.md."""

    date: str  # YYYY-MM-DD format
    times: str  # e.g., "11:30 PM - 7:00 AM"
    display: str  # e.g., "2024-01-15: 11:30 PM - 7:00 AM"


@dataclass
class SleepInputData:
    """All collected sleep input data to pass to the script."""

    sleep_wake_times: str  # The sleep/wake time string with date prefix
    quality: Optional[str]  # Excellent, Good, Fair, Poor, Restless, or None (Skip)
    had_dreams: bool  # Whether user had dreams
    dream_descriptions: str  # Multi-line dream descriptions (empty if no dreams)


class SleepInputDialog(QDialog):
    """Dialog for collecting all sleep-related inputs."""

    QUALITY_OPTIONS: list[str] = [
        "Excellent",
        "Good",
        "Fair",
        "Poor",
        "Restless",
        "Skip",
    ]

    def __init__(self, config: Config, parent=None) -> None:
        super().__init__(parent)
        self.config = config
        self.time_entries: list[TimeEntry] = []
        self.collected_data: Optional[SleepInputData] = None
        self._was_custom_selected: bool = False

        self.setWindowTitle(f"Sleep Entry - {APP_NAME}")
        self.setMinimumSize(600, 330)

        self._load_time_entries()
        self._setup_ui()
        self._center_window()

    def _load_time_entries(self) -> None:
        """Load and parse time entries from Time.md in the vault."""
        time_file_path: Optional[Path] = self.config.get_time_path()

        if not time_file_path or not time_file_path.exists():
            return

        try:
            content: str = time_file_path.read_text(encoding="utf-8")
            lines: list[str] = content.split("\n")

            # Parse lines matching: [[YYYY-MM-DD]]: times or [YYYY-MM-DD]: times
            pattern = re.compile(r"\[\[?(\d{4}-\d{2}-\d{2})\]?\]?:\s*(.+)")

            for line in lines:
                line: str = line.strip()
                if not line:
                    continue

                match = pattern.match(line)
                if match:
                    date = match.group(1)
                    times = match.group(2).strip()
                    self.time_entries.append(
                        TimeEntry(
                            date=date,
                            times=times,
                            display=f"{date}: {times}",
                        )
                    )

            # Sort by date (most recent first)
            self.time_entries.sort(key=lambda x: x.date, reverse=True)

        except Exception:
            # If we can't read the file, just continue with empty entries
            pass

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
        sections_layout = QVBoxLayout(sections_container)
        sections_layout.setContentsMargins(0, 0, 0, 0)
        sections_layout.setSpacing(0)

        # === Sleep & Wake Time Section ===
        time_section = SettingsGroup("Sleep & Wake Time", parent=sections_container)
        time_section.setSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum
        )
        time_content = QWidget()
        time_layout = QVBoxLayout(time_content)
        time_layout.setContentsMargins(8, 8, 8, 8)
        time_layout.setSpacing(12)

        if self.time_entries:
            self.time_combo = QComboBox()
            self.time_combo.setFont(QFont(FONT_FAMILY, 10))
            self.time_combo.setProperty("MainComboBox", True)
            self.time_combo.setMinimumHeight(32)
            self.time_combo.addItem("Select a time entry", None)
            self.time_combo.setToolTip("Select from Time.md or enter custom time")

            for entry in self.time_entries:
                self.time_combo.addItem(entry.display, entry)

            self.time_combo.addItem("✏️ Custom time entry", "CUSTOM")
            self.time_combo.currentIndexChanged.connect(self._on_time_selection_changed)
            time_layout.addWidget(self.time_combo)

            # Custom time input (hidden by default)
            self.custom_time_widget = QWidget()
            custom_layout = QVBoxLayout(self.custom_time_widget)
            custom_layout.setContentsMargins(0, 8, 0, 0)
            custom_layout.setSpacing(8)

            custom_label = QLabel(
                "Format: @YYYY-MM-DD or @MM-DD or @DD HH:MM AM/PM - HH:MM AM/PM"
            )
            custom_label.setFont(QFont(FONT_FAMILY, 9))
            custom_label.setStyleSheet(
                f"color: {THEME_TEXT_SECONDARY}; font-weight: bold;"
            )
            custom_layout.addWidget(custom_label)

            self.custom_time_input = QLineEdit()
            self.custom_time_input.setProperty("MainLineEdit", True)
            self.custom_time_input.setPlaceholderText("e.g., @15 11:30 PM - 7:00 AM")
            self.custom_time_input.setMinimumHeight(32)
            custom_layout.addWidget(self.custom_time_input)

            self.custom_time_widget.setVisible(False)
            time_layout.addWidget(self.custom_time_widget)
        else:
            # No Time.md entries, show only custom input
            info_label = QLabel(
                "Format: @YYYY-MM-DD or @MM-DD or @DD HH:MM AM/PM - HH:MM AM/PM"
            )
            info_label.setFont(QFont(FONT_FAMILY, 9))
            info_label.setStyleSheet(f"color: {THEME_TEXT_SECONDARY};")
            time_layout.addWidget(info_label)

            self.time_combo = None
            self.custom_time_widget = None

            self.custom_time_input = QLineEdit()
            self.custom_time_input.setProperty("MainLineEdit", True)
            self.custom_time_input.setPlaceholderText("e.g., @15 11:30 PM - 7:00 AM")
            self.custom_time_input.setMinimumHeight(32)
            time_layout.addWidget(self.custom_time_input)

        time_section.setLayout(time_layout)
        sections_layout.addWidget(time_section)

        # === Sleep Quality Section ===
        quality_section = SettingsGroup("Sleep Quality", parent=sections_container)
        quality_section.setSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum
        )
        quality_content = QWidget()
        quality_layout = QVBoxLayout(quality_content)
        quality_layout.setContentsMargins(8, 8, 8, 8)
        quality_layout.setSpacing(12)

        self.quality_combo = QComboBox()
        self.quality_combo.setProperty("MainComboBox", True)
        self.quality_combo.setFont(QFont(FONT_FAMILY, 10))
        self.quality_combo.setMinimumHeight(32)
        for option in self.QUALITY_OPTIONS:
            self.quality_combo.addItem(option, option if option != "Skip" else None)
        self.quality_combo.setCurrentIndex(1)  # Default to "Good"
        quality_layout.addWidget(self.quality_combo)

        quality_section.setLayout(quality_layout)
        sections_layout.addWidget(quality_section)

        # === Dreams Section ===
        self.dreams_section = SettingsGroup("Dreams", parent=sections_container)
        self.dreams_section.setSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum
        )
        dreams_content = QWidget()
        dreams_layout = QVBoxLayout(dreams_content)
        dreams_layout.setContentsMargins(8, 8, 8, 8)
        dreams_layout.setSpacing(12)

        # Yes/No radio buttons
        dream_question = QLabel("Did you have any dreams?")
        dream_question.setFont(QFont(FONT_FAMILY, 10))
        dream_question.setStyleSheet(f"color: {THEME_TEXT_SECONDARY};")
        dreams_layout.addWidget(dream_question)

        radio_layout = QHBoxLayout()
        radio_layout.setSpacing(12)
        radio_layout.setContentsMargins(0, 0, 0, 0)

        self.dream_button_group = QButtonGroup(self)
        self.dream_yes_radio = QRadioButton("Yes")
        self.dream_yes_radio.setFont(QFont(FONT_FAMILY, 10))
        self.dream_yes_radio.setIcon(get_icon("square_check.svg", color=THEME_BORDER))
        self.dream_yes_radio.setIconSize(QSize(20, 20))

        self.dream_no_radio = QRadioButton("No")
        self.dream_no_radio.setFont(QFont(FONT_FAMILY, 10))
        self.dream_no_radio.setIcon(get_icon("square_check.svg", color=THEME_BORDER))
        self.dream_no_radio.setIconSize(QSize(20, 20))
        self.dream_no_radio.setChecked(True)  # Default to No

        self.dream_button_group.addButton(self.dream_yes_radio, 1)
        self.dream_button_group.addButton(self.dream_no_radio, 0)

        # Connect to update icons when checked state changes
        self.dream_button_group.buttonClicked.connect(self._update_radio_icons)

        radio_layout.addWidget(self.dream_yes_radio)
        radio_layout.addWidget(self.dream_no_radio)
        radio_layout.addStretch()
        dreams_layout.addLayout(radio_layout)

        # Dream descriptions (shown when Yes is selected)
        self.dream_input_widget = QWidget()
        self.dream_input_widget.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        dream_input_layout = QVBoxLayout(self.dream_input_widget)
        dream_input_layout.setContentsMargins(0, 12, 0, 0)
        dream_input_layout.setSpacing(8)

        dream_input_label = QLabel("Describe your dreams:")
        dream_input_label.setFont(QFont(FONT_FAMILY, 9))
        dream_input_label.setStyleSheet(f"color: {THEME_TEXT_SECONDARY};")
        dream_input_layout.addWidget(dream_input_label)

        self.dream_text_edit = QTextEdit()
        self.dream_text_edit.setFont(QFont(FONT_FAMILY, 10))
        self.dream_text_edit.setPlaceholderText("Enter each dream on a new line...")
        self.dream_text_edit.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        self.dream_text_edit.setMinimumHeight(100)
        dream_input_layout.addWidget(self.dream_text_edit)

        self.dream_input_widget.setVisible(False)
        dreams_layout.addWidget(self.dream_input_widget)

        # Connect radio button changes
        self.dream_button_group.buttonClicked.connect(self._on_dream_selection_changed)

        # Set initial icons
        self._update_radio_icons()

        self.dreams_section.setLayout(dreams_layout)
        sections_layout.addWidget(self.dreams_section, stretch=0)

        # Add a stretch item to absorb extra space
        # This will be given high priority when dreams section is collapsed
        sections_layout.addStretch(1)

        # Store reference to the layout for dynamic management
        self.sections_layout = sections_layout

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

        submit_btn = HoverIconButton(
            normal_icon=Icons.SAVE,
            hover_icon=Icons.CONTENT_SAVE,
            pressed_icon=Icons.CONTENT_SAVE_CHECK,
            text="  Save Entry",
        )
        submit_btn.setProperty("SaveButton", True)
        submit_btn.setFont(QFont(FONT_FAMILY, 10))
        submit_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        submit_btn.setFixedHeight(30)
        submit_btn.setShortcut(QKeySequence("Ctrl+Return"))
        submit_btn.clicked.connect(self._on_submit)
        button_layout.addWidget(submit_btn)

        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)

    def _on_time_selection_changed(self) -> None:
        """Handle time dropdown selection change."""
        if self.custom_time_widget is None:
            return

        data = self.time_combo.currentData()
        if data == "CUSTOM":
            self.custom_time_widget.setVisible(True)
            self.dreams_section.setSizePolicy(
                QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding
            )
            self.setMinimumHeight(406)

            # Defer centering until after layout updates
            QTimer.singleShot(0, self._center_window)

            self._was_custom_selected = True
            self.custom_time_input.setFocus()
        else:
            self.dreams_section.setSizePolicy(
                QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum
            )
            self.setMinimumHeight(330)
            self.resize(self.width(), 330)

            # Only center when transitioning FROM custom TO regular entry
            if self._was_custom_selected:
                QTimer.singleShot(0, self._center_window)

            self._was_custom_selected = False
            self.custom_time_widget.setVisible(False)

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

    def _on_dream_selection_changed(self) -> None:
        """Handle dream yes/no selection change."""
        if self.dream_yes_radio.isChecked():
            self.dream_input_widget.setVisible(True)
            self.dreams_section.setSizePolicy(
                QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding
            )
            # Give dreams section stretch priority (index 2 is dreams_section)
            self.sections_layout.setStretch(2, 1)
            self.sections_layout.setStretch(3, 0)  # Bottom spacer gets no priority
            self.setMinimumHeight(570)

            # Defer centering until after layout updates
            QTimer.singleShot(0, self._center_window)

            self.dream_text_edit.setFocus()
        else:
            self.dream_input_widget.setVisible(False)
            self.dreams_section.setSizePolicy(
                QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum
            )
            # Give bottom spacer stretch priority
            self.sections_layout.setStretch(2, 0)  # Dreams section gets no priority
            self.sections_layout.setStretch(3, 1)  # Bottom spacer absorbs space
            self.setMinimumHeight(330)
            self.resize(self.width(), 330)

            # Defer centering until after layout updates
            QTimer.singleShot(0, self._center_window)

    def _update_radio_icons(self) -> None:
        """Update radio button icons based on checked state."""
        # Update Yes radio
        if self.dream_yes_radio.isChecked():
            self.dream_yes_radio.setIcon(
                get_icon("square_check_filled.svg", color=COLOR_LIGHT_BLUE)
            )
        else:
            self.dream_yes_radio.setIcon(
                get_icon("square_check.svg", color=THEME_BORDER)
            )

        # Update No radio
        if self.dream_no_radio.isChecked():
            self.dream_no_radio.setIcon(
                get_icon("square_check_filled.svg", color=COLOR_LIGHT_BLUE)
            )
        else:
            self.dream_no_radio.setIcon(
                get_icon("square_check.svg", color=THEME_BORDER)
            )

    def _on_submit(self) -> None:
        """Validate and collect all input data."""
        # Get sleep/wake time
        sleep_wake_times = ""

        if self.time_combo is not None:
            data = self.time_combo.currentData()
            if data is None:
                # No selection made
                QMessageBox.warning(
                    self, "Missing Input", "Please select a time entry."
                )
                return
            elif data == "CUSTOM":
                # Using custom input
                custom_text = self.custom_time_input.text().strip()
                if not custom_text:
                    QMessageBox.warning(
                        self, "Missing Input", "Please enter a custom time."
                    )
                    return
                sleep_wake_times = custom_text
            else:
                # Using selected entry from Time.md
                entry: TimeEntry = data
                sleep_wake_times: str = f"@{entry.date} {entry.times}"
        else:
            # Only custom input available
            custom_text: str = self.custom_time_input.text().strip()
            if not custom_text:
                QMessageBox.warning(
                    self, "Missing Input", "Please enter sleep and wake times."
                )
                return
            sleep_wake_times = custom_text

        # Get quality
        quality = self.quality_combo.currentData()

        # Get dreams info
        had_dreams: bool = self.dream_yes_radio.isChecked()
        dream_descriptions = ""
        if had_dreams:
            dream_descriptions: str = self.dream_text_edit.toPlainText().strip()

        # Store collected data
        self.collected_data = SleepInputData(
            sleep_wake_times=sleep_wake_times,
            quality=quality,
            had_dreams=had_dreams,
            dream_descriptions=dream_descriptions,
        )

        self.accept()

    def get_collected_data(self) -> Optional[SleepInputData]:
        """Return the collected sleep input data."""
        return self.collected_data
