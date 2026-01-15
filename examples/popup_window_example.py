"""
Example usage of PopupWindow component.
Demonstrates different popup styles and configurations.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from PySide6.QtWidgets import QApplication, QPushButton, QVBoxLayout, QWidget

from src.ui.popup_window import PopupIcon, PopupWindow
from src.ui.styles import get_main_stylesheet


class PopupDemo(QWidget):
    """Demo window showing various popup configurations."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Popup Window Examples")
        self.setMinimumSize(400, 300)

        layout = QVBoxLayout()

        # Info popup
        info_btn = QPushButton("Show Info Popup")
        info_btn.clicked.connect(self.show_info_popup)
        layout.addWidget(info_btn)

        # Warning popup
        warning_btn = QPushButton("Show Warning Popup")
        warning_btn.clicked.connect(self.show_warning_popup)
        layout.addWidget(warning_btn)

        # Error popup
        error_btn = QPushButton("Show Error Popup")
        error_btn.clicked.connect(self.show_error_popup)
        layout.addWidget(error_btn)

        # Success popup
        success_btn = QPushButton("Show Success Popup")
        success_btn.clicked.connect(self.show_success_popup)
        layout.addWidget(success_btn)

        # Confirmation popup (OK/Cancel)
        confirm_btn = QPushButton("Show Confirmation Popup")
        confirm_btn.clicked.connect(self.show_confirmation_popup)
        layout.addWidget(confirm_btn)

        # Custom buttons popup
        custom_btn = QPushButton("Show Custom Buttons Popup")
        custom_btn.clicked.connect(self.show_custom_buttons_popup)
        layout.addWidget(custom_btn)

        # No icon popup
        no_icon_btn = QPushButton("Show No Icon Popup")
        no_icon_btn.clicked.connect(self.show_no_icon_popup)
        layout.addWidget(no_icon_btn)

        layout.addStretch()
        self.setLayout(layout)

    def show_info_popup(self):
        """Show an info popup."""
        popup = PopupWindow(
            message="This is an informational message.\nIt uses the info icon and only has an OK button.",
            title="Information",
            icon=PopupIcon.INFO,
            info_popup=True,
            parent=self,
        )
        popup.exec()

    def show_warning_popup(self):
        """Show a warning popup."""
        popup = PopupWindow(
            message="This is a warning message.\nSomething requires your attention!",
            title="Warning",
            icon=PopupIcon.WARNING,
            info_popup=True,
            parent=self,
        )
        popup.exec()

    def show_error_popup(self):
        """Show an error popup."""
        popup = PopupWindow(
            message="An error has occurred!\nPlease check the logs for more details.",
            title="Error",
            icon=PopupIcon.ERROR,
            info_popup=True,
            parent=self,
        )
        popup.exec()

    def show_success_popup(self):
        """Show a success popup."""
        popup = PopupWindow(
            message="Operation completed successfully!\nAll changes have been saved.",
            title="Success",
            icon=PopupIcon.SUCCESS,
            info_popup=True,
            parent=self,
        )
        popup.exec()

    def show_confirmation_popup(self):
        """Show a confirmation popup with OK and Cancel buttons."""
        popup = PopupWindow(
            message="Are you sure you want to proceed?\nThis action cannot be undone.",
            title="Confirm Action",
            icon=PopupIcon.WARNING,
            info_popup=False,  # This will show OK and Cancel buttons
            parent=self,
        )

        # Connect signals to handle user choice
        popup.accepted.connect(lambda: print("User clicked OK"))
        popup.cancelled.connect(lambda: print("User clicked Cancel"))

        popup.exec()

    def show_custom_buttons_popup(self):
        """Show a popup with custom buttons."""
        popup = PopupWindow(
            message="Choose your preferred option from the buttons below.",
            title="Custom Options",
            icon=PopupIcon.INFO,
            buttons=["Option A", "Option B", "Option C"],
            parent=self,
        )

        # Connect to custom signal
        popup.custom_signal.connect(lambda label: print(f"User selected: {label}"))

        popup.exec()

    def show_no_icon_popup(self):
        """Show a popup without an icon."""
        popup = PopupWindow(
            message="This popup has no icon, just a simple message.",
            title="No Icon",
            icon=PopupIcon.NONE,
            info_popup=True,
            parent=self,
        )
        popup.exec()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Apply Tokyo Night theme
    app.setStyleSheet(get_main_stylesheet())

    demo = PopupDemo()
    demo.show()

    sys.exit(app.exec())
