"""
System tray manager for Obsidian Forge.
Handles tray icon, context menu, and notifications.
"""

from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMenu, QSystemTrayIcon

from src.core import ScriptExecutor
from src.utils import get_icon


class SystemTrayManager(QObject):
    """Manages system tray icon and interactions."""

    # Signals
    show_window_requested = Signal()
    hide_window_requested = Signal()
    settings_requested = Signal()
    about_requested = Signal()
    exit_requested = Signal()
    script_execution_requested = Signal(str, str)  # script_name, script_path
    search_scripts_requested = Signal()

    def __init__(self, executor: ScriptExecutor, parent=None) -> None:
        super().__init__(parent)
        self.executor = executor
        self.tray_icon = None
        self.tray_menu = None
        self.show_hide_action = None
        self._setup_tray()

    def _setup_tray(self) -> None:
        """Initialize system tray icon and menu."""
        # Create tray icon
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(get_icon("application/obsidian_forge.svg"))
        self.tray_icon.setToolTip("Obsidian Forge")

        # Connect activation signal (double-click)
        self.tray_icon.activated.connect(self._on_tray_activated)

        # Create context menu
        self._create_context_menu()

        # Set menu and show
        self.tray_icon.setContextMenu(self.tray_menu)
        self.tray_icon.show()

    def _create_context_menu(self) -> None:
        """Create tray icon context menu."""
        self.tray_menu = QMenu()

        # Show/Hide action
        self.show_hide_action = QAction("Show Window", self)
        self.show_hide_action.triggered.connect(self._toggle_window)
        self.tray_menu.addAction(self.show_hide_action)

        self.tray_menu.addSeparator()

        # Search Scripts action
        search_scripts_action = QAction("Search Scripts...", self)
        search_scripts_action.triggered.connect(self.search_scripts_requested.emit)
        self.tray_menu.addAction(search_scripts_action)

        self.tray_menu.addSeparator()

        # Settings action
        settings_action = QAction("Settings", self)
        settings_action.triggered.connect(self.settings_requested.emit)
        self.tray_menu.addAction(settings_action)

        # About action
        about_action = QAction("About", self)
        about_action.triggered.connect(self.about_requested.emit)
        self.tray_menu.addAction(about_action)

        self.tray_menu.addSeparator()

        # Exit action
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.exit_requested.emit)
        self.tray_menu.addAction(exit_action)

    def _on_tray_activated(self, reason) -> None:
        """Handle tray icon activation."""
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self._toggle_window()

    def _toggle_window(self) -> None:
        """Toggle window visibility."""
        # This will be connected to MainWindow's show/hide logic
        self.show_window_requested.emit()

    def update_show_hide_text(self, window_visible: bool) -> None:
        """Update Show/Hide action text based on window state."""
        if window_visible:
            self.show_hide_action.setText("Hide Window")
        else:
            self.show_hide_action.setText("Show Window")

    def show_notification(
        self,
        title: str,
        message: str,
        icon_type=QSystemTrayIcon.MessageIcon.Information,
    ) -> None:
        """Show system tray notification."""
        if self.tray_icon:
            self.tray_icon.showMessage(title, message, icon_type, 100)
