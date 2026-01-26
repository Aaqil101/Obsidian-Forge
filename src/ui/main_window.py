"""
Main application window for Obsidian Forge.
Styled with Tokyo Night theme following GitUI's design patterns.
"""

# ----- Built-In Modules-----
from pathlib import Path

# ----- PySide6 Modules-----
from PySide6.QtCore import QEasingCurve, QPropertyAnimation, QSize, Qt, QThread, Signal
from PySide6.QtGui import QCursor, QFont, QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QScrollArea,
    QTextEdit,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

# ----- Core Modules-----
from src.core import (
    APP_NAME,
    FONT_FAMILY,
    WINDOW_MIN_HEIGHT,
    WINDOW_MIN_WIDTH,
    Config,
    ScriptExecutor,
    SleepScriptInputs,
)

# ----- UI Modules-----
from src.ui import components
from src.ui.about_dialog import AboutDialog
from src.ui.popup_window import PopupIcon, PopupWindow
from src.ui.settings_dialog import SettingsDialog
from src.ui.sleep_dialog import SleepInputDialog
from src.ui.widgets import ScriptRow, SettingsGroup

# ----- Utils Modules-----
from src.utils import THEME_TEXT_PRIMARY, HoverIconButton, Icons, get_icon


class ExpandableSearchBar(QLineEdit):
    """Search bar that expands from the right when hovered or focused."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.collapsed_width = 32
        self.expanded_width = 250
        self.is_expanded = False

        # Setup animations
        self.width_animation = QPropertyAnimation(self, b"minimumWidth")
        self.width_animation.setDuration(200)
        self.width_animation.setEasingCurve(QEasingCurve.Type.OutCubic)

        self.max_width_animation = QPropertyAnimation(self, b"maximumWidth")
        self.max_width_animation.setDuration(200)
        self.max_width_animation.setEasingCurve(QEasingCurve.Type.OutCubic)

        # Initial state - collapsed
        self.setFixedWidth(self.collapsed_width)
        self.setPlaceholderText("")

    def expand(self) -> None:
        """Expand the search bar."""
        if not self.is_expanded:
            self.is_expanded = True
            self.setPlaceholderText("Search scripts... (Ctrl+F)")

            # Animate width
            self.width_animation.setStartValue(self.collapsed_width)
            self.width_animation.setEndValue(self.expanded_width)
            self.max_width_animation.setStartValue(self.collapsed_width)
            self.max_width_animation.setEndValue(self.expanded_width)

            self.width_animation.start()
            self.max_width_animation.start()

    def collapse(self) -> None:
        """Collapse the search bar if not focused and empty."""
        if self.is_expanded and not self.hasFocus() and not self.text():
            self.is_expanded = False
            self.setPlaceholderText("")

            # Animate width
            self.width_animation.setStartValue(self.expanded_width)
            self.width_animation.setEndValue(self.collapsed_width)
            self.max_width_animation.setStartValue(self.expanded_width)
            self.max_width_animation.setEndValue(self.collapsed_width)

            self.width_animation.start()
            self.max_width_animation.start()

    def enterEvent(self, event) -> None:
        """Expand on hover."""
        self.expand()
        super().enterEvent(event)

    def leaveEvent(self, event) -> None:
        """Collapse on leave if not focused and empty."""
        self.collapse()
        super().leaveEvent(event)

    def focusInEvent(self, event) -> None:
        """Expand on focus."""
        self.expand()
        super().focusInEvent(event)

    def focusOutEvent(self, event) -> None:
        """Collapse on focus out if empty."""
        self.collapse()
        super().focusOutEvent(event)


class ScriptThread(QThread):
    """Thread for executing scripts without blocking the UI."""

    finished = Signal(dict)

    def __init__(
        self, executor: ScriptExecutor, script_path: Path, user_input: str
    ) -> None:
        super().__init__()
        self.executor: ScriptExecutor = executor
        self.script_path: Path = script_path
        self.user_input: str = user_input

    def run(self) -> None:
        """Execute the script."""
        result = self.executor.execute_script(self.script_path, self.user_input)
        self.finished.emit(result)


class SleepScriptThread(QThread):
    """Thread for executing the sleep script with pre-collected inputs."""

    finished = Signal(dict)

    def __init__(
        self, executor: ScriptExecutor, script_path: Path, sleep_inputs
    ) -> None:
        super().__init__()
        self.executor: ScriptExecutor = executor
        self.script_path: Path = script_path
        self.sleep_inputs = sleep_inputs

    def run(self) -> None:
        """Execute the sleep script."""
        inputs = SleepScriptInputs(
            sleep_wake_times=self.sleep_inputs.sleep_wake_times,
            quality=self.sleep_inputs.quality,
            had_dreams=self.sleep_inputs.had_dreams,
            dream_descriptions=self.sleep_inputs.dream_descriptions,
        )
        result = self.executor.execute_sleep_script(self.script_path, inputs)
        self.finished.emit(result)


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self) -> None:
        super().__init__()
        self.config = Config()
        self.executor = ScriptExecutor(self.config)
        self.script_thread = None

        self.setWindowTitle(APP_NAME)
        self.setWindowIcon(get_icon("application/obsidian_forge.svg"))
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)
        self.setMinimumSize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)

        self.setup_ui()
        self.setup_menu()
        self.setup_shortcuts()

        # Center the window on the screen
        self.center_on_screen()

        # Check if configured
        if not self.config.is_configured():
            self.show_settings()

    def center_on_screen(self) -> None:
        """Center the window on the screen."""
        screen = self.screen()
        if screen:
            screen_geometry = screen.availableGeometry()
            window_geometry = self.frameGeometry()
            center_point = screen_geometry.center()
            window_geometry.moveCenter(center_point)
            self.move(window_geometry.topLeft())

    def create_menu_item(
        self, icon_name: str, text: str, shortcut: str = ""
    ) -> QWidget:
        """Create a custom menu item widget with icon and text."""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(8)

        # Icon
        icon_label = QLabel()
        icon_label.setPixmap(get_icon(icon_name).pixmap(QSize(16, 16)))
        icon_label.setFixedSize(16, 16)
        layout.addWidget(icon_label)

        # Text
        text_label = QLabel(text)
        layout.addWidget(text_label)

        # Spacer
        layout.addStretch()

        # Shortcut
        if shortcut:
            shortcut_label = QLabel(shortcut)
            layout.addWidget(shortcut_label)

        return widget

    def setup_menu(self) -> None:
        """Setup keyboard shortcuts."""
        # Setup keyboard shortcuts
        self.settings_shortcut = QShortcut(QKeySequence("Ctrl+,"), self)
        self.settings_shortcut.activated.connect(self.show_settings)

        self.exit_shortcut = QShortcut(QKeySequence("Ctrl+Q"), self)
        self.exit_shortcut.activated.connect(self.close)

    def setup_shortcuts(self) -> None:
        """Setup keyboard shortcuts for navigation."""
        # Focus search bar
        search_shortcut = QShortcut(QKeySequence("Ctrl+F"), self)
        search_shortcut.activated.connect(lambda: self.search_input.setFocus())

    def setup_ui(self) -> None:
        """Setup the user interface with Blender-Launcher-inspired design."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Header bar with search and action buttons
        header_widget = QWidget()
        header_widget.setObjectName("HeaderBar")
        header_widget.setFixedHeight(32)

        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(0)

        # Settings button
        settings_btn = QToolButton()
        settings_btn.setIcon(get_icon("settings.svg"))
        settings_btn.setProperty("MainToolButton", True)
        settings_btn.setIconSize(QSize(20, 20))
        settings_btn.setToolTip("Settings (Ctrl+,)")
        settings_btn.setFixedSize(32, 32)
        settings_btn.clicked.connect(self.show_settings)
        header_layout.addWidget(settings_btn)

        # About button
        about_btn = QToolButton()
        about_btn.setIcon(get_icon("about.svg"))
        about_btn.setProperty("MainToolButton", True)
        about_btn.setIconSize(QSize(20, 20))
        about_btn.setToolTip("About")
        about_btn.setFixedSize(32, 32)
        about_btn.clicked.connect(self.show_about)
        header_layout.addWidget(about_btn)

        # Add stretch to push search bar to the right
        header_layout.addStretch()

        # Search bar - expandable from the right
        self.search_input = ExpandableSearchBar()
        self.search_input.setFont(QFont(FONT_FAMILY, 10))
        self.search_input.setProperty("SearchBar", True)
        self.search_input.textChanged.connect(self.filter_scripts)
        self.search_input.setFixedHeight(32)
        self.search_input.addAction(
            get_icon("search.svg", THEME_TEXT_PRIMARY),
            QLineEdit.ActionPosition.LeadingPosition,
        )
        self.search_input.setTextMargins(0, 0, 0, 0)
        header_layout.addWidget(self.search_input)

        main_layout.addWidget(header_widget)

        # Content container
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(8, 8, 8, 8)
        content_layout.setSpacing(8)

        # Scroll area for script sections
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)

        # Container for all sections
        self.sections_container = QWidget()
        self.sections_layout = QVBoxLayout(self.sections_container)
        self.sections_layout.setContentsMargins(0, 0, 0, 0)
        self.sections_layout.setSpacing(0)

        # Store all script rows for filtering
        self.all_script_rows = []

        # Daily Notes Section
        self.create_collapsible_section("Daily Notes", "daily")

        # Weekly Notes Section
        self.create_collapsible_section("Weekly Notes", "weekly")

        # Add stretch at the end
        self.sections_layout.addStretch()

        scroll_area.setWidget(self.sections_container)
        content_layout.addWidget(scroll_area)

        main_layout.addWidget(content_widget)
        central_widget.setLayout(main_layout)

    def create_collapsible_section(self, title: str, script_type: str) -> None:
        """Create a collapsible section with script cards in a grid layout."""
        # Create collapsible settings group
        section_group = SettingsGroup(title, parent=self.sections_container)

        # Create container for script cards with grid layout
        cards_widget = QWidget()
        cards_widget.setProperty("CardsContainer", True)
        cards_layout = QGridLayout(cards_widget)
        cards_layout.setContentsMargins(6, 6, 6, 6)
        cards_layout.setSpacing(8)

        # Get scripts and create cards in grid (5 columns)
        scripts = self.executor.get_available_scripts(script_type)
        columns = 5
        for index, script in enumerate(scripts):
            row: int = index // columns
            col: int = index % columns

            script_row = ScriptRow(
                name=script["name"],
                icon_name=script["icon"],
                description=f"Execute {script['name']} script",
                script_type=script_type,
                parent=cards_widget,
            )
            # Connect to run script
            script_row.execute_clicked.connect(
                lambda s=script: self.run_script(s["name"], s["path"])
            )
            cards_layout.addWidget(script_row, row, col)

            # Store for filtering
            self.all_script_rows.append(
                (script_row, script["name"].lower(), script_type)
            )

        # Set the content widget
        section_group.setWidget(cards_widget)

        # Add to main layout
        self.sections_layout.addWidget(section_group)

    def filter_scripts(self, text: str) -> None:
        """Filter script rows based on search text."""
        search_text: str = text.lower().strip()
        for script_row, name, script_type in self.all_script_rows:
            if search_text == "" or search_text in name or search_text in script_type:
                script_row.setVisible(True)
            else:
                script_row.setVisible(False)

    def run_script(self, script_name: str, script_path: str) -> None:
        """Run a script after getting user input."""
        if not self.config.is_configured():
            popup = PopupWindow(
                message="Please configure the application settings first.",
                title="Configuration Required",
                icon=PopupIcon.WARNING,
                info_popup=True,
                parent=self,
            )
            popup.accepted.connect(self.show_settings)
            popup.exec()
            return

        # Check if this is the sleep script - it needs special handling
        if script_name.lower() == "sleep":
            self._run_sleep_script(script_path)
            return

        # Create input dialog for other scripts
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Add {script_name}")
        dialog.setMinimumSize(550, 450)

        layout = QVBoxLayout()
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)

        # Instruction label
        if "daily" in script_path.lower():
            instruction: str = (
                f"Enter your {script_name.lower()} (one per line).\n"
                "Use @YYYY-MM-DD, @MM-DD, or @DD to specify a date.\n"
                "If no date is specified, today's date will be used."
            )
        else:
            instruction = (
                f"Enter your {script_name.lower()} (one per line).\n"
                "Use @YYYY-Www or @ww to specify a week.\n"
                "If no week is specified, the current week will be used."
            )

        label = components.create_info_label(instruction)
        layout.addWidget(label)

        # Text input
        text_edit = QTextEdit()
        text_edit.setFont(QFont(FONT_FAMILY, 10))
        text_edit.setPlaceholderText("Type here...")
        text_edit.setFocus()
        layout.addWidget(text_edit)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 4, 0, 0)
        button_layout.setSpacing(8)
        button_layout.addStretch()

        # Cancel button
        cancel_btn = HoverIconButton(
            normal_icon=Icons.CANCEL_OUTLINE, hover_icon=Icons.CANCEL, text="&Cancel"
        )
        cancel_btn.setFont(QFont(FONT_FAMILY, 10))
        cancel_btn.setProperty("CancelButton", True)
        cancel_btn.setShortcut(QKeySequence("Esc"))
        cancel_btn.setFixedHeight(36)
        cancel_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        cancel_btn.clicked.connect(dialog.reject)
        button_layout.addWidget(cancel_btn)

        # Submit button
        submit_btn = HoverIconButton(
            normal_icon=Icons.SAVE,
            hover_icon=Icons.CONTENT_SAVE,
            pressed_icon=Icons.CONTENT_SAVE_CHECK,
            text="&Save",
        )
        submit_btn.setFont(QFont(FONT_FAMILY, 10))
        submit_btn.setProperty("SaveButton", True)
        submit_btn.setFixedHeight(36)
        submit_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        submit_btn.setDefault(True)
        submit_btn.setShortcut(QKeySequence("Ctrl+Return"))
        submit_btn.clicked.connect(dialog.accept)
        button_layout.addWidget(submit_btn)

        layout.addLayout(button_layout)
        dialog.setLayout(layout)

        # Center dialog on parent window
        parent_geometry = self.frameGeometry()
        dialog_geometry = dialog.frameGeometry()
        center_point = parent_geometry.center()
        dialog_geometry.moveCenter(center_point)
        dialog.move(dialog_geometry.topLeft())

        # Show dialog
        if dialog.exec() == QDialog.DialogCode.Accepted:
            user_input: str = text_edit.toPlainText().strip()
            if user_input:
                self.execute_script(script_path, user_input)

    def _run_sleep_script(self, script_path: str) -> None:
        """Run the sleep script with special input collection dialog."""
        dialog = SleepInputDialog(self.config, self)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            sleep_data = dialog.get_collected_data()
            if sleep_data:
                self._execute_sleep_script(script_path, sleep_data)

    def _execute_sleep_script(self, script_path: str, sleep_data) -> None:
        """Execute the sleep script in a background thread."""
        if self.script_thread and self.script_thread.isRunning():
            popup = PopupWindow(
                message="A script is already running. Please wait for it to complete.",
                title="Script Running",
                icon=PopupIcon.WARNING,
                info_popup=True,
                parent=self,
            )
            popup.exec()
            return

        # Disable UI
        self.setEnabled(False)
        self.statusBar().showMessage("Adding sleep entry...")

        # Create and start thread
        self.script_thread = SleepScriptThread(
            self.executor, Path(script_path), sleep_data
        )
        self.script_thread.finished.connect(self.on_script_finished)
        self.script_thread.start()

    def execute_script(self, script_path: str, user_input: str) -> None:
        """Execute a script in a background thread."""
        if self.script_thread and self.script_thread.isRunning():
            popup = PopupWindow(
                message="A script is already running. Please wait for it to complete.",
                title="Script Running",
                icon=PopupIcon.WARNING,
                info_popup=True,
                parent=self,
            )
            popup.exec()
            return

        # Disable UI
        self.setEnabled(False)
        self.statusBar().showMessage("Executing script...")

        # Create and start thread
        self.script_thread = ScriptThread(self.executor, Path(script_path), user_input)
        self.script_thread.finished.connect(self.on_script_finished)
        self.script_thread.start()

    def on_script_finished(self, result: dict) -> None:
        """Handle script execution completion."""
        # Re-enable UI
        self.setEnabled(True)
        self.statusBar().clearMessage()

        if result["success"]:
            popup = PopupWindow(
                message=result["output"] or "Script executed successfully!",
                title="Success",
                icon=PopupIcon.SUCCESS,
                info_popup=True,
                parent=self,
            )
            popup.exec()
        else:
            popup = PopupWindow(
                message=f"Script execution failed:\n\n{result['error']}",
                title="Error",
                icon=PopupIcon.ERROR,
                info_popup=True,
                parent=self,
            )
            popup.exec()

    def show_settings(self) -> None:
        """Show the settings dialog."""
        dialog = SettingsDialog(self.config, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Refresh the UI to load new scripts
            self.refresh_ui()

    def refresh_ui(self) -> None:
        """Refresh the UI after settings change."""
        # Clear existing script rows
        self.all_script_rows.clear()

        # Clear the sections layout
        while self.sections_layout.count() > 0:
            item = self.sections_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Recreate sections
        self.create_collapsible_section("Daily Notes", "daily")
        self.create_collapsible_section("Weekly Notes", "weekly")
        self.sections_layout.addStretch()

    def show_about(self) -> None:
        """Show the about dialog."""
        dialog = AboutDialog(self)
        dialog.exec()
