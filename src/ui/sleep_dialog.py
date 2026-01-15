"""
Sleep input dialog for collecting all sleep-related inputs upfront.
This dialog pre-collects all the data needed by the add-daily-sleep.js script.
"""

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from PySide6.QtGui import QKeySequence
from PySide6.QtWidgets import (
    QButtonGroup,
    QComboBox,
    QDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QRadioButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from src.core.config import (
    FONT_SIZE_SMALL,
    PADDING,
    PADDING_LARGE,
    SPACING,
    SPACING_LARGE,
    SPACING_SMALL,
    TIME_PATH,
    Config,
)
from src.ui import components
from src.utils import THEME_TEXT_SECONDARY, Icons


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

    QUALITY_OPTIONS = ["Excellent", "Good", "Fair", "Poor", "Restless", "Skip"]

    def __init__(self, config: Config, parent=None) -> None:
        super().__init__(parent)
        self.config = config
        self.time_entries: list[TimeEntry] = []
        self.collected_data: Optional[SleepInputData] = None

        self.setWindowTitle("Add Sleep Entry")
        self.setMinimumSize(500, 550)

        self._load_time_entries()
        self._setup_ui()

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
        """Setup the dialog UI."""
        layout = QVBoxLayout()
        layout.setContentsMargins(
            PADDING_LARGE, PADDING_LARGE, PADDING_LARGE, PADDING_LARGE
        )
        layout.setSpacing(SPACING_LARGE)

        # === Time Selection Section ===
        time_group = QGroupBox("Sleep & Wake Time")
        time_layout = QVBoxLayout()
        time_layout.setSpacing(SPACING)
        time_layout.setContentsMargins(PADDING, PADDING, PADDING, PADDING)

        if self.time_entries:
            # Show dropdown with entries from Time.md
            info_label = QLabel("Select from Time.md or enter custom time:")
            info_label.setStyleSheet(
                f"color: {THEME_TEXT_SECONDARY}; font-size: {FONT_SIZE_SMALL}px;"
            )
            time_layout.addWidget(info_label)

            self.time_combo = QComboBox()
            self.time_combo.addItem("-- Select a time entry --", None)
            for entry in self.time_entries:
                self.time_combo.addItem(entry.display, entry)
            self.time_combo.addItem("✏️ Custom time entry", "CUSTOM")
            self.time_combo.currentIndexChanged.connect(self._on_time_selection_changed)
            time_layout.addWidget(self.time_combo)

            # Custom time input (hidden by default)
            self.custom_time_widget = QWidget()
            custom_layout = QVBoxLayout(self.custom_time_widget)
            custom_layout.setContentsMargins(0, SPACING_SMALL, 0, 0)
            custom_layout.setSpacing(SPACING_SMALL)

            custom_label = QLabel(
                "Format: @YYYY-MM-DD or @MM-DD or @DD HH:MM AM/PM - HH:MM AM/PM"
            )
            custom_label.setStyleSheet(
                f"color: {THEME_TEXT_SECONDARY}; font-size: {FONT_SIZE_SMALL}px;"
            )
            custom_layout.addWidget(custom_label)

            self.custom_time_input = QLineEdit()
            self.custom_time_input.setPlaceholderText("e.g., @15 11:30 PM - 7:00 AM")
            custom_layout.addWidget(self.custom_time_input)

            self.custom_time_widget.setVisible(False)
            time_layout.addWidget(self.custom_time_widget)
        else:
            # No Time.md entries, show only custom input
            info_label = QLabel(
                "Time.md not found or empty. Enter sleep time manually:\n"
                "Format: @YYYY-MM-DD or @MM-DD or @DD HH:MM AM/PM - HH:MM AM/PM"
            )
            info_label.setWordWrap(True)
            info_label.setStyleSheet(
                f"color: {THEME_TEXT_SECONDARY}; font-size: {FONT_SIZE_SMALL}px;"
            )
            time_layout.addWidget(info_label)

            self.time_combo = None
            self.custom_time_widget = None

            self.custom_time_input = QLineEdit()
            self.custom_time_input.setPlaceholderText("e.g., @15 11:30 PM - 7:00 AM")
            time_layout.addWidget(self.custom_time_input)

        time_group.setLayout(time_layout)
        layout.addWidget(time_group)

        # === Sleep Quality Section ===
        quality_group = QGroupBox("Sleep Quality")
        quality_layout = QVBoxLayout()
        quality_layout.setSpacing(SPACING_SMALL)
        quality_layout.setContentsMargins(PADDING, PADDING, PADDING, PADDING)

        self.quality_combo = QComboBox()
        for option in self.QUALITY_OPTIONS:
            self.quality_combo.addItem(option, option if option != "Skip" else None)
        self.quality_combo.setCurrentIndex(1)  # Default to "Good"
        quality_layout.addWidget(self.quality_combo)

        quality_group.setLayout(quality_layout)
        layout.addWidget(quality_group)

        # === Dreams Section ===
        dreams_group = QGroupBox("Dreams")
        dreams_layout = QVBoxLayout()
        dreams_layout.setSpacing(SPACING)
        dreams_layout.setContentsMargins(PADDING, PADDING, PADDING, PADDING)

        # Yes/No radio buttons
        dream_question = QLabel("Did you have any dreams?")
        dreams_layout.addWidget(dream_question)

        radio_layout = QHBoxLayout()
        radio_layout.setSpacing(SPACING_LARGE)

        self.dream_button_group = QButtonGroup(self)
        self.dream_yes_radio = QRadioButton("Yes")
        self.dream_no_radio = QRadioButton("No")
        self.dream_no_radio.setChecked(True)  # Default to No

        self.dream_button_group.addButton(self.dream_yes_radio, 1)
        self.dream_button_group.addButton(self.dream_no_radio, 0)

        radio_layout.addWidget(self.dream_yes_radio)
        radio_layout.addWidget(self.dream_no_radio)
        radio_layout.addStretch()
        dreams_layout.addLayout(radio_layout)

        # Dream descriptions (shown when Yes is selected)
        self.dream_input_widget = QWidget()
        dream_input_layout = QVBoxLayout(self.dream_input_widget)
        dream_input_layout.setContentsMargins(0, SPACING_SMALL, 0, 0)
        dream_input_layout.setSpacing(SPACING_SMALL)

        dream_input_label = QLabel("Describe your dreams (one per line):")
        dream_input_label.setStyleSheet(
            f"color: {THEME_TEXT_SECONDARY}; font-size: {FONT_SIZE_SMALL}px;"
        )
        dream_input_layout.addWidget(dream_input_label)

        self.dream_text_edit = QTextEdit()
        self.dream_text_edit.setPlaceholderText("Enter each dream on a new line...")
        self.dream_text_edit.setMinimumHeight(80)
        dream_input_layout.addWidget(self.dream_text_edit)

        self.dream_input_widget.setVisible(False)
        dreams_layout.addWidget(self.dream_input_widget)

        # Connect radio button changes
        self.dream_button_group.buttonClicked.connect(self._on_dream_selection_changed)

        dreams_group.setLayout(dreams_layout)
        layout.addWidget(dreams_group)

        layout.addStretch()

        # === Buttons ===
        button_layout = QHBoxLayout()
        button_layout.setSpacing(SPACING_SMALL)
        button_layout.addStretch()

        cancel_btn = components.create_secondary_button("Cancel", Icons.CANCEL)
        cancel_btn.setShortcut(QKeySequence("Esc"))
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        submit_btn = components.create_primary_button("Submit", Icons.CHECK)
        submit_btn.setShortcut(QKeySequence("Ctrl+Return"))
        submit_btn.clicked.connect(self._on_submit)
        button_layout.addWidget(submit_btn)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def _on_time_selection_changed(self, index: int) -> None:
        """Handle time dropdown selection change."""
        if self.custom_time_widget is None:
            return

        data = self.time_combo.currentData()
        if data == "CUSTOM":
            self.custom_time_widget.setVisible(True)
            self.custom_time_input.setFocus()
        else:
            self.custom_time_widget.setVisible(False)

    def _on_dream_selection_changed(self) -> None:
        """Handle dream yes/no selection change."""
        if self.dream_yes_radio.isChecked():
            self.dream_input_widget.setVisible(True)
            self.dream_text_edit.setFocus()
        else:
            self.dream_input_widget.setVisible(False)

    def _on_submit(self) -> None:
        """Validate and collect all input data."""
        # Get sleep/wake time
        sleep_wake_times = ""

        if self.time_combo is not None:
            data = self.time_combo.currentData()
            if data is None:
                # No selection made
                from PySide6.QtWidgets import QMessageBox

                QMessageBox.warning(
                    self, "Missing Input", "Please select a time entry."
                )
                return
            elif data == "CUSTOM":
                # Using custom input
                custom_text = self.custom_time_input.text().strip()
                if not custom_text:
                    from PySide6.QtWidgets import QMessageBox

                    QMessageBox.warning(
                        self, "Missing Input", "Please enter a custom time."
                    )
                    return
                sleep_wake_times = custom_text
            else:
                # Using selected entry from Time.md
                entry: TimeEntry = data
                sleep_wake_times = f"@{entry.date} {entry.times}"
        else:
            # Only custom input available
            custom_text = self.custom_time_input.text().strip()
            if not custom_text:
                from PySide6.QtWidgets import QMessageBox

                QMessageBox.warning(
                    self, "Missing Input", "Please enter sleep and wake times."
                )
                return
            sleep_wake_times = custom_text

        # Get quality
        quality = self.quality_combo.currentData()

        # Get dreams info
        had_dreams = self.dream_yes_radio.isChecked()
        dream_descriptions = ""
        if had_dreams:
            dream_descriptions = self.dream_text_edit.toPlainText().strip()

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
