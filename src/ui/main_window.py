"""
Main application window for Obsidian Forge.
Styled with Tokyo Night theme following GitUI's design patterns.
"""

# ----- Built-In Modules-----
from pathlib import Path

# ----- PySide6 Modules-----
from PySide6.QtCore import QSize, Qt, QThread, Signal
from PySide6.QtGui import QAction, QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

# ----- Core Modules-----
from src.core import (
    ANIMATION_DURATION,
    APP_NAME,
    APP_VERSION,
    AUTHOR,
    BORDER_RADIUS,
    BORDER_RADIUS_LARGE,
    BORDER_RADIUS_SMALL,
    DAILY_SCRIPTS_PATH,
    FONT_FAMILY,
    FONT_SIZE_HEADER,
    FONT_SIZE_LABEL,
    FONT_SIZE_SMALL,
    FONT_SIZE_TEXT,
    FONT_SIZE_TITLE,
    HOVER_DURATION,
    PADDING,
    PADDING_LARGE,
    PADDING_SMALL,
    SPACING,
    SPACING_LARGE,
    SPACING_SMALL,
    UTILS_SCRIPTS_PATH,
    WEEKLY_SCRIPTS_PATH,
    WINDOW_MIN_HEIGHT,
    WINDOW_MIN_WIDTH,
    Config,
    ScriptExecutor,
)

# ----- UI Modules-----
from src.ui import components
from src.ui.settings_dialog import SettingsDialog

# ----- Utils Modules-----
from src.utils import Icons, get_icon


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


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self) -> None:
        super().__init__()
        self.config = Config()
        self.executor = ScriptExecutor(self.config)
        self.script_thread = None

        self.setWindowTitle(APP_NAME)
        self.setWindowIcon(get_icon("obsidian-forge.svg"))
        self.setMinimumSize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)

        self.setup_ui()
        self.setup_menu()
        self.setup_shortcuts()

        # Check if configured
        if not self.config.is_configured():
            self.show_settings()

    def setup_menu(self) -> None:
        """Setup the menu bar."""
        menubar = self.menuBar()

        # ---------- File menu ----------
        file_menu = menubar.addMenu("&File")

        settings_action = QAction("Settings", self)
        settings_action.setIcon(get_icon("settings.svg"))
        settings_action.setShortcut("Ctrl+,")
        settings_action.setStatusTip("Open application settings")
        settings_action.triggered.connect(self.show_settings)
        file_menu.addAction(settings_action)

        file_menu.addSeparator()

        exit_action = QAction(f"{Icons.EXIT}  Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.setStatusTip("Exit the application")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # ---------- Help menu ----------
        help_menu = menubar.addMenu("&Help")

        about_action = QAction(f"{Icons.INFO}  About", self)
        about_action.setStatusTip("About this application")
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def setup_shortcuts(self) -> None:
        """Setup keyboard shortcuts for navigation."""
        # Tab navigation shortcuts
        next_tab = QShortcut(QKeySequence("Ctrl+Tab"), self)
        next_tab.activated.connect(self.next_tab)

        prev_tab = QShortcut(QKeySequence("Ctrl+Shift+Tab"), self)
        prev_tab.activated.connect(self.prev_tab)

        # Alt+1 for Daily Notes tab
        daily_shortcut = QShortcut(QKeySequence("Alt+1"), self)
        daily_shortcut.activated.connect(lambda: self.tab_widget.setCurrentIndex(0))

        # Alt+2 for Weekly Notes tab
        weekly_shortcut = QShortcut(QKeySequence("Alt+2"), self)
        weekly_shortcut.activated.connect(lambda: self.tab_widget.setCurrentIndex(1))

    def next_tab(self) -> None:
        """Switch to next tab."""
        current: int = self.tab_widget.currentIndex()
        count: int = self.tab_widget.count()
        self.tab_widget.setCurrentIndex((current + 1) % count)

    def prev_tab(self) -> None:
        """Switch to previous tab."""
        current: int = self.tab_widget.currentIndex()
        count: int = self.tab_widget.count()
        self.tab_widget.setCurrentIndex((current - 1) % count)

    def setup_ui(self) -> None:
        """Setup the user interface."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(PADDING, PADDING, PADDING, PADDING)
        main_layout.setSpacing(SPACING)

        # Header
        header_label = components.create_header_label(APP_NAME, FONT_SIZE_TITLE)
        main_layout.addWidget(header_label)

        subtitle_label = components.create_subtitle_label(
            "Add bullet points to your Daily and Weekly notes"
        )
        main_layout.addWidget(subtitle_label)

        # Tab widget for Daily and Weekly
        self.tab_widget = QTabWidget()
        self.tab_widget.addTab(
            self.create_daily_tab(), f"{Icons.CALENDAR_DAY}  Daily Notes"
        )
        self.tab_widget.addTab(
            self.create_weekly_tab(), f"{Icons.CALENDAR_WEEK}  Weekly Notes"
        )

        main_layout.addWidget(self.tab_widget)

        central_widget.setLayout(main_layout)

    def create_daily_tab(self) -> QWidget:
        """Create the daily notes tab."""
        return self.create_sidebar_view_tab("daily")

    def create_sidebar_view_tab(self, script_type: str) -> QWidget:
        """Create a sidebar view tab."""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(
            PADDING_SMALL,
            PADDING_SMALL,
            PADDING_SMALL,
            PADDING_SMALL,
        )
        layout.setSpacing(SPACING_SMALL)

        # Sidebar list
        list_widget = QListWidget()
        list_widget.setProperty("ScriptList", True)

        # Load and create list items for scripts
        scripts = self.executor.get_available_scripts(script_type)
        for script in scripts:
            item = QListWidgetItem(f"{script['icon']}  {script['name']}")
            item.setData(Qt.ItemDataRole.UserRole, script["path"])
            list_widget.addItem(item)

        list_widget.itemClicked.connect(
            lambda item: self.run_script(
                item.text().split("  ", 1)[1], item.data(Qt.ItemDataRole.UserRole)
            )
        )
        layout.addWidget(list_widget)

        widget.setLayout(layout)
        return widget

    def create_weekly_tab(self) -> QWidget:
        """Create the weekly notes tab."""
        return self.create_sidebar_view_tab("weekly")

    def run_script(self, script_name: str, script_path: str) -> None:
        """Run a script after getting user input."""
        if not self.config.is_configured():
            QMessageBox.warning(
                self,
                "Configuration Required",
                "Please configure the application settings first.",
            )
            self.show_settings()
            return

        # Create input dialog
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Add {script_name}")
        dialog.setMinimumSize(550, 400)

        layout = QVBoxLayout()
        layout.setContentsMargins(
            PADDING_LARGE,
            PADDING_LARGE,
            PADDING_LARGE,
            PADDING_LARGE,
        )
        layout.setSpacing(SPACING_LARGE)

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
        text_edit.setPlaceholderText("Type here...")
        text_edit.setFocus()
        layout.addWidget(text_edit)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(SPACING_SMALL)
        button_layout.addStretch()

        cancel_btn = components.create_secondary_button("Cancel", Icons.CANCEL)
        cancel_btn.setShortcut(QKeySequence("Esc"))
        cancel_btn.clicked.connect(dialog.reject)
        button_layout.addWidget(cancel_btn)

        submit_btn = components.create_primary_button("Submit", Icons.CHECK)
        submit_btn.setShortcut(QKeySequence("Ctrl+Return"))
        submit_btn.clicked.connect(dialog.accept)
        button_layout.addWidget(submit_btn)

        layout.addLayout(button_layout)
        dialog.setLayout(layout)

        # Show dialog
        if dialog.exec() == QDialog.DialogCode.Accepted:
            user_input: str = text_edit.toPlainText().strip()
            if user_input:
                self.execute_script(script_path, user_input)

    def execute_script(self, script_path: str, user_input: str) -> None:
        """Execute a script in a background thread."""
        if self.script_thread and self.script_thread.isRunning():
            QMessageBox.warning(
                self,
                "Script Running",
                "A script is already running. Please wait for it to complete.",
            )
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
            QMessageBox.information(
                self,
                f"{Icons.CHECK}  Success",
                result["output"] or "Script executed successfully!",
            )
        else:
            QMessageBox.critical(
                self,
                f"{Icons.CROSS}  Error",
                f"Script execution failed:\n\n{result['error']}",
            )

    def show_settings(self) -> None:
        """Show the settings dialog."""
        dialog = SettingsDialog(self.config, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Refresh the UI to load new scripts
            self.refresh_ui()

    def refresh_ui(self) -> None:
        """Refresh the UI after settings change."""
        # Recreate tabs
        self.tab_widget.clear()
        self.tab_widget.addTab(
            self.create_daily_tab(), f"{Icons.CALENDAR_DAY}  Daily Notes"
        )
        self.tab_widget.addTab(
            self.create_weekly_tab(), f"{Icons.CALENDAR_WEEK}  Weekly Notes"
        )

    def show_about(self) -> None:
        """Show the about dialog."""
        QMessageBox.about(
            self,
            f"About {APP_NAME}",
            f"<h2>{APP_NAME}</h2>"
            "<p>A PySide6 application for adding bullet points to Obsidian daily and weekly notes.</p>"
            f"<p>Version {APP_VERSION}</p>"
            "<p>Uses your existing QuickAdd JavaScript scripts.</p>"
            "<p>Styled with Tokyo Night theme.</p>"
            f"<p> Created by: {AUTHOR}</p>",
        )
