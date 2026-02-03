"""
Main application window for Obsidian Forge.
Styled with Tokyo Night theme following GitUI's design patterns.
"""

# ----- Built-In Modules-----
import os
import sys
import webbrowser
from pathlib import Path

# ----- Keyboard Modules-----
import keyboard

# ----- PySide6 Modules-----
from PySide6.QtCore import QEasingCurve, QPropertyAnimation, QSize, Qt, QThread, Signal
from PySide6.QtGui import QCursor, QFont, QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QScrollArea,
    QSystemTrayIcon,
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

# ----- Core Modules-----
from src.core.config import APP_NAME, FONT_FAMILY, Config
from src.core.flask_server import FlaskServerThread

# ----- UI Modules-----
from src.ui import components
from src.ui.about_dialog import AboutDialog
from src.ui.frontmatter import DailyFrontmatterDialog, WeeklyFrontmatterDialog
from src.ui.popup_window import PopupIcon, PopupWindow
from src.ui.search_dialog import ScriptSearchDialog
from src.ui.settings_dialog import SettingsDialog
from src.ui.sleep_dialog import SleepInputDialog
from src.ui.system_tray import SystemTrayManager

# ----- UI Modules-----
from src.ui.widgets import ScriptRow, SettingsGroup

# ----- Utils Modules-----
from src.utils import (
    COLOR_GREEN,
    COLOR_RED,
    THEME_TEXT_PRIMARY,
    HoverIconButtonSVG,
    get_icon,
)


class ExpandableSearchBar(QLineEdit):
    """Search bar that expands from the right when hovered or focused."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.collapsed_width = 32
        self.expanded_width = 250
        self.is_expanded = False
        self.main_window = None  # Will be set by MainWindow

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
            self.setToolTip(
                "Filter by section:\n/D - Show daily notes only\n/W - Show weekly notes only\n\nExample: /D win (searches 'win' in daily notes)"
            )

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

    def keyPressEvent(self, event) -> None:
        """Handle Enter key to execute single search result."""
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            if self.main_window:
                self.main_window.execute_single_search_result()
            event.accept()
        else:
            super().keyPressEvent(event)


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

    # Signal for thread-safe script search dialog opening
    open_script_search_signal = Signal()

    def __init__(self) -> None:
        super().__init__()
        self.config = Config()
        self.executor = ScriptExecutor(self.config)
        self.script_thread = None
        self.flask_server_thread = None
        self.keyboard_hotkey_registered = False

        # Connect the signal to the method for thread-safe access
        self.open_script_search_signal.connect(
            self._show_script_search, Qt.ConnectionType.QueuedConnection
        )

        # Setup system tray
        self.tray_manager = SystemTrayManager(self.executor, self)
        self._setup_tray_connections()

        # Script search dialog (lazy initialization)
        self.script_search_dialog = None

        # Connect to app quit signal for cleanup
        QApplication.instance().aboutToQuit.connect(self.cleanup_on_exit)

        # Track window visibility state
        self._is_window_visible = True

        self.setWindowTitle(APP_NAME)
        self.setWindowIcon(get_icon("application/obsidian_forge.svg"))
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)
        self.setMinimumSize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)

        self.setup_ui()
        self.setup_menu()
        self.setup_shortcuts()
        self.setup_global_hotkeys()

        # Center the window on the screen
        self.center_on_screen()

        # Check if configured
        if not self.config.is_configured():
            self.show_settings()

    def _setup_tray_connections(self) -> None:
        """Connect system tray signals to MainWindow slots."""
        self.tray_manager.show_window_requested.connect(self._toggle_window_visibility)
        self.tray_manager.settings_requested.connect(self.show_settings)
        self.tray_manager.about_requested.connect(self.show_about)
        self.tray_manager.exit_requested.connect(self._exit_application)
        self.tray_manager.script_execution_requested.connect(self._execute_from_tray)
        self.tray_manager.search_scripts_requested.connect(self._show_script_search)

    def _toggle_window_visibility(self) -> None:
        """Toggle window show/hide state."""
        if self.isVisible():
            self.hide()
            self._is_window_visible = False
            self.tray_manager.update_show_hide_text(False)
        else:
            self.show()
            self.activateWindow()
            self.raise_()
            self._is_window_visible = True
            self.tray_manager.update_show_hide_text(True)

    def _execute_from_tray(self, script_name: str, script_path: str) -> None:
        """Execute a script from the tray menu."""
        # Show window first to ensure proper parent for dialogs
        if not self.isVisible():
            self._toggle_window_visibility()
        # Execute the script normally
        self.run_script(script_name, script_path)

    def _show_script_search(self) -> None:
        """Show the script search dialog from tray."""
        # Lazy initialization
        if self.script_search_dialog is None:
            self.script_search_dialog = ScriptSearchDialog(self.executor, self)
            self.script_search_dialog.script_selected.connect(self._execute_from_search)
            self.script_search_dialog.frontmatter_edit_requested.connect(
                lambda note_type: self.show_frontmatter_editor(note_type)
            )
            self.script_search_dialog.restart_requested.connect(
                self._restart_application
            )
            self.script_search_dialog.exit_requested.connect(self._exit_application)

        # Show and activate the dialog
        self.script_search_dialog.show()
        self.script_search_dialog.activateWindow()
        self.script_search_dialog.raise_()

    def _execute_from_search(self, script_name: str, script_path: str) -> None:
        """Execute a script selected from search dialog."""
        # Hide search dialog
        if self.script_search_dialog:
            self.script_search_dialog.hide()

        # Execute the script directly - dialogs can appear without showing main window
        self.run_script(script_name, script_path)

    def _restart_application(self) -> None:
        """Restart the application."""
        # Clean up keyboard hooks before restart
        self.cleanup_global_hotkeys()

        # Close the current application
        QApplication.quit()

        # Start a new instance
        if getattr(sys, "frozen", False):
            # Running as compiled executable
            os.execl(sys.executable, sys.executable, *sys.argv)
        else:
            # Running as script
            python = sys.executable
            script = sys.argv[0]
            os.execl(python, python, script, *sys.argv[1:])

    def _exit_application(self) -> None:
        """Properly exit the application."""
        self.cleanup_global_hotkeys()
        QApplication.quit()

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

        self.esc_shortcut = QShortcut(QKeySequence("Esc"), self)
        self.esc_shortcut.activated.connect(self.close)

    def setup_shortcuts(self) -> None:
        """Setup keyboard shortcuts for navigation."""
        # Focus search bar
        search_shortcut = QShortcut(QKeySequence("Ctrl+F"), self)
        search_shortcut.activated.connect(lambda: self.search_input.setFocus())

    def setup_global_hotkeys(self) -> None:
        """Setup global hotkeys that work even when app is minimized."""
        try:
            # Register Win+Space to open script search
            # Use signal emission for thread-safe Qt interaction
            keyboard.add_hotkey(
                "win+space",
                lambda: self.open_script_search_signal.emit(),
                suppress=False,
            )
            self.keyboard_hotkey_registered = True
        except ImportError:
            # keyboard library not installed, skip global hotkeys
            print("Warning: 'keyboard' library not installed. Global hotkeys disabled.")
        except Exception as e:
            # Failed to register hotkey (maybe permissions issue)
            print(f"Warning: Failed to register global hotkey: {e}")

    def cleanup_global_hotkeys(self) -> None:
        """Clean up global hotkeys on application exit."""
        if self.keyboard_hotkey_registered:
            try:
                keyboard.unhook_all()
            except Exception:
                pass  # Ignore cleanup errors

    def cleanup_on_exit(self) -> None:
        """Clean up resources when application is about to quit."""
        # Stop Flask server if running
        if self.flask_server_thread and self.flask_server_thread.isRunning():
            self.flask_server_thread.stop()
            self.flask_server_thread.wait(2000)  # Wait up to 2 seconds

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
        self.search_input.main_window = self  # Set reference to main window
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

        # Store all script rows for filtering (script_row, name, script_type)
        self.all_script_rows = []
        # Store script information for execution (script_row -> script info)
        self.script_row_map = {}

        # Daily Notes Section
        self.create_collapsible_section("Daily Notes", "daily")

        # Weekly Notes Section
        self.create_collapsible_section("Weekly Notes", "weekly")

        # Libraries Section
        self.create_libraries_section()

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

        # Add frontmatter edit button to section header
        section_group.setActionButton(
            "edit.svg", f"Edit {script_type.title()} Note Frontmatter"
        )
        section_group.action_clicked.connect(
            lambda st=script_type: self.show_frontmatter_editor(st)
        )

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
            # Store script info for execution
            self.script_row_map[script_row] = script

        # Set the content widget
        section_group.setWidget(cards_widget)

        # Add to main layout
        self.sections_layout.addWidget(section_group)

    def create_libraries_section(self) -> None:
        """Create a collapsible section with media library cards."""
        # Create collapsible settings group
        section_group = SettingsGroup("Libraries", parent=self.sections_container)

        # Create container for library cards with grid layout
        cards_widget = QWidget()
        cards_widget.setProperty("CardsContainer", True)
        cards_layout = QGridLayout(cards_widget)
        cards_layout.setContentsMargins(6, 6, 6, 6)
        cards_layout.setSpacing(8)

        # Define media library items
        libraries = [
            {"name": "Books", "icon": "web/books.svg", "type": "books"},
            {"name": "Movies", "icon": "web/movies.svg", "type": "movies"},
            {"name": "TV Shows", "icon": "web/tv_shows.svg", "type": "tv_shows"},
            {"name": "YouTube Videos", "icon": "web/youtube.svg", "type": "youtube"},
            {
                "name": "Documentaries",
                "icon": "web/documentaries.svg",
                "type": "documentaries",
            },
        ]

        # Create cards in grid (5 columns)
        columns = 5
        for index, library in enumerate(libraries):
            row: int = index // columns
            col: int = index % columns

            library_row = ScriptRow(
                name=library["name"],
                icon_name=library["icon"],
                description=f"Open {library['name']} library",
                script_type="library",
                parent=cards_widget,
            )
            # Connect to launch media library
            library_row.execute_clicked.connect(
                lambda t=library["type"]: self.launch_media_library(t)
            )
            cards_layout.addWidget(library_row, row, col)

        # Set the content widget
        section_group.setWidget(cards_widget)

        # Add to main layout
        self.sections_layout.addWidget(section_group)

    def filter_scripts(self, text: str) -> None:
        """Filter script rows based on search text with support for D: and W: prefixes."""
        search_text: str = text.lower().strip()

        # Check for filter prefix
        filter_type = None
        if search_text.startswith("/d"):
            filter_type = "daily"
            search_text = search_text[2:].strip()
        elif search_text.startswith("/w"):
            filter_type = "weekly"
            search_text = search_text[2:].strip()

        for script_row, name, script_type in self.all_script_rows:
            # First check if section filter matches
            if filter_type and script_type != filter_type:
                script_row.setVisible(False)
                continue

            # Then check if search text matches
            if search_text == "" or search_text in name or search_text in script_type:
                script_row.setVisible(True)
            else:
                script_row.setVisible(False)

    def execute_single_search_result(self) -> None:
        """Execute the script if there's only one visible search result."""
        visible_scripts = [
            (script_row, name, script_type)
            for script_row, name, script_type in self.all_script_rows
            if script_row.isVisible()
        ]

        # Only execute if there's exactly one visible result
        if len(visible_scripts) == 1:
            script_row = visible_scripts[0][0]
            # Get the script info and execute it
            script = self.script_row_map.get(script_row)
            if script:
                self.run_script(script["name"], script["path"])

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
        cancel_btn.clicked.connect(dialog.reject)
        button_layout.addWidget(cancel_btn)

        # Submit button
        submit_btn = HoverIconButtonSVG(
            normal_icon="save_outline.svg",
            normal_color=f"{COLOR_GREEN}",
            hover_icon="save_filled.svg",
            hover_color=f"{COLOR_GREEN}",
            pressed_icon="save_check_filled.svg",
            pressed_color=f"{COLOR_GREEN}",
            icon_size=14,
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
            message = result["output"] or "Script executed successfully!"

            # Show tray notification
            self.tray_manager.show_notification(
                "Script Success",
                message,
                QSystemTrayIcon.MessageIcon.Information,
            )

            # Show popup if window is visible
            if self._is_window_visible:
                popup = PopupWindow(
                    message=message,
                    title="Success",
                    icon=PopupIcon.SUCCESS,
                    info_popup=True,
                    parent=self,
                )
                popup.exec()
        else:
            error_msg = f"Script execution failed:\n\n{result['error']}"

            # Show tray notification (truncate for notification)
            self.tray_manager.show_notification(
                "Script Error",
                result["error"][:100],
                QSystemTrayIcon.MessageIcon.Critical,
            )

            # Show popup if window is visible
            if self._is_window_visible:
                popup = PopupWindow(
                    message=error_msg,
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
        self.script_row_map.clear()

        # Clear the sections layout
        while self.sections_layout.count() > 0:
            item = self.sections_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Recreate sections
        self.create_collapsible_section("Daily Notes", "daily")
        self.create_collapsible_section("Weekly Notes", "weekly")
        self.sections_layout.addStretch()

        # Clear cached search dialog to reload scripts
        if self.script_search_dialog:
            self.script_search_dialog.deleteLater()
            self.script_search_dialog = None

    def show_about(self) -> None:
        """Show the about dialog."""
        dialog = AboutDialog(self)
        dialog.exec()

    def launch_media_library(self, media_type: str = "") -> None:
        """Launch the media library in browser, filtered to media type."""
        if not self.config.is_configured():
            popup = PopupWindow(
                message="Please configure vault path in settings first.",
                title="Configuration Required",
                icon=PopupIcon.WARNING,
                parent=self,
            )
            popup.exec()
            return

        # Start server if not running
        if self.flask_server_thread is None or not self.flask_server_thread.isRunning():
            self._start_flask_server(media_type)
        else:
            # Server already running, just open browser
            port = self.flask_server_thread.port
            url = f"http://127.0.0.1:{port}"
            if media_type:
                url += f"?type={media_type}"
            webbrowser.open(url)

    def _start_flask_server(self, media_type: str = "") -> None:
        """Start Flask server in background thread."""
        self.flask_server_thread = FlaskServerThread(self.config, self)
        self.flask_server_thread.server_started.connect(
            lambda port: self._on_flask_server_started(port, media_type)
        )
        self.flask_server_thread.server_error.connect(self._on_flask_server_error)
        self.flask_server_thread.start()

    def _on_flask_server_started(self, port: int, media_type: str = "") -> None:
        """Handle successful server start."""
        url = f"http://127.0.0.1:{port}"
        if media_type:
            url += f"?type={media_type}"
        webbrowser.open(url)

        self.tray_manager.show_notification(
            "Media Library",
            f"Server started on port {port}",
            QSystemTrayIcon.MessageIcon.Information,
        )

    def _on_flask_server_error(self, error: str) -> None:
        """Handle server error."""
        popup = PopupWindow(
            message=f"Failed to start media library server:\n\n{error}",
            title="Server Error",
            icon=PopupIcon.ERROR,
            parent=self,
        )
        popup.exec()

    def show_frontmatter_editor(self, note_type: str = "daily") -> None:
        """
        Show the frontmatter editing dialog.

        Args:
            note_type: Type of note to edit - "daily" or "weekly"
        """
        if not self.config.vault_path:
            popup = PopupWindow(
                message="Please configure your Obsidian vault path in settings first.",
                title="No Vault",
                icon=PopupIcon.WARNING,
                parent=self,
            )
            popup.exec()
            return

        if note_type == "daily":
            dialog = DailyFrontmatterDialog(self.config, parent=self)
        else:  # weekly
            dialog = WeeklyFrontmatterDialog(self.config, parent=self)
        dialog.exec()

    def closeEvent(self, event) -> None:
        """Handle window close event - minimize to tray or close fully with Shift."""
        # Check if Shift key is held down
        modifiers = QApplication.keyboardModifiers()
        if modifiers & Qt.KeyboardModifier.ShiftModifier:
            # Shift+Click = fully close the application
            self.cleanup_global_hotkeys()

            # Stop Flask server if running
            if self.flask_server_thread and self.flask_server_thread.isRunning():
                self.flask_server_thread.stop()
                self.flask_server_thread.wait(2000)  # Wait up to 2 seconds

            event.accept()
            QApplication.quit()
        else:
            # Normal close = minimize to tray
            event.ignore()  # Don't actually close
            self.hide()
            self._is_window_visible = False
            self.tray_manager.update_show_hide_text(False)

            # Show notification on first minimize
            if not hasattr(self, "_first_minimize_shown"):
                self.tray_manager.show_notification(
                    "Obsidian Forge",
                    "Application minimized to system tray. Double-click the tray icon to restore.\nTip: Hold Shift while clicking close to exit completely.",
                    QSystemTrayIcon.MessageIcon.Information,
                )
                self._first_minimize_shown = True
