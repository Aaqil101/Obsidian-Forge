"""
Obsidian Forge - Main entry point
A PySide6 application for adding bullet points to Obsidian daily and weekly notes.
Styled with Tokyo Night theme following GitUI's design patterns.
"""

# ----- Built-In Modules-----
import sys
from pathlib import Path

# ----- PySide6 Modules-----
from PySide6.QtWidgets import QApplication, QSystemTrayIcon

# ----- Resources-----
# Import Qt compiled resources (needed for :/assets/ paths in stylesheets)
import src.resources_rc  # noqa: F401

# ----- Core Modules-----
from src.core.config import APP_NAME, Config

# ----- UI Modules-----
from src.ui import MainWindow
from src.ui.styles.build_styles import build_stylesheet

# ----- Utils Modules-----
from src.utils import get_icon


def main():
    """Main entry point for the application."""
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setOrganizationName(APP_NAME.replace(" ", ""))

    # Set application icon
    app.setWindowIcon(get_icon("application/obsidian_forge.svg"))

    # Apply stylesheet to entire application
    app.setStyleSheet(build_stylesheet())

    # Create main window
    window = MainWindow()

    # Check if should start minimized
    config = Config()

    if not config.start_minimized:
        window.show()
    else:
        # Window is created but hidden - tray icon is already visible
        window.tray_manager.show_notification(
            "Obsidian Forge",
            "Application started in background. Double-click tray icon to open.",
            QSystemTrayIcon.MessageIcon.Information,
        )

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
