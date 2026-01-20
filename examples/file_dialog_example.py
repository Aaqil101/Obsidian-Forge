"""
Example usage of styled QFileDialog component.
Demonstrates different file dialog configurations with Tokyo Night theme.
"""

# ----- Built-In Modules-----
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# ----- PySide6 Modules-----
from PySide6.QtWidgets import QApplication, QPushButton, QVBoxLayout, QWidget

# ----- UI Modules-----
from src.ui import (
    FileDialog,
    open_file_dialog,
    save_file_dialog,
    select_directory_dialog,
)


class FileDialogDemo(QWidget):
    """Demo window showing various file dialog configurations."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("File Dialog Examples")
        self.setMinimumSize(400, 300)

        layout = QVBoxLayout()

        # Example 1: Simple file open dialog (convenience function)
        btn1 = QPushButton("Open Single File (Quick)")
        btn1.clicked.connect(self.example_open_file_quick)
        layout.addWidget(btn1)

        # Example 2: Multiple file selection (convenience function)
        btn2 = QPushButton("Open Multiple Files (Quick)")
        btn2.clicked.connect(self.example_open_files_quick)
        layout.addWidget(btn2)

        # Example 3: Save file dialog (convenience function)
        btn3 = QPushButton("Save File (Quick)")
        btn3.clicked.connect(self.example_save_file_quick)
        layout.addWidget(btn3)

        # Example 4: Directory selection (convenience function)
        btn4 = QPushButton("Select Directory (Quick)")
        btn4.clicked.connect(self.example_select_directory_quick)
        layout.addWidget(btn4)

        # Example 5: Multiple directory selection (convenience function)
        btn5 = QPushButton("Select Multiple Directories (Quick)")
        btn5.clicked.connect(self.example_select_directories_quick)
        layout.addWidget(btn5)

        # Example 6: Using FileDialog class with custom configuration
        btn6 = QPushButton("Open File (Class Instance)")
        btn6.clicked.connect(self.example_file_dialog_class)
        layout.addWidget(btn6)

        self.setLayout(layout)

    def example_open_file_quick(self) -> None:
        """Example: Open single file using convenience function."""
        files = open_file_dialog(
            parent=self,
            title="Select a Python File",
            file_filter="Python Files (*.py);;All Files (*.*)",
        )
        if files:
            print(f"Selected file: {files[0]}")

    def example_open_files_quick(self) -> None:
        """Example: Open multiple files using convenience function."""
        files = open_file_dialog(
            parent=self,
            title="Select Multiple Files",
            file_filter="All Files (*.*)",
            multi_select=True,
        )
        if files:
            print(f"Selected {len(files)} file(s):")
            for file in files:
                print(f"  - {file}")

    def example_save_file_quick(self) -> None:
        """Example: Save file using convenience function."""
        file_path = save_file_dialog(
            parent=self,
            title="Save Configuration",
            file_filter="JSON Files (*.json);;All Files (*.*)",
            default_name="config.json",
        )
        if file_path:
            print(f"Save to: {file_path}")

    def example_select_directory_quick(self) -> None:
        """Example: Select directory using convenience function."""
        directories = select_directory_dialog(
            parent=self,
            title="Select Project Directory",
        )
        if directories:
            print(f"Selected directory: {directories[0]}")

    def example_select_directories_quick(self) -> None:
        """Example: Select multiple directories using convenience function."""
        directories = select_directory_dialog(
            parent=self,
            title="Select Multiple Directories",
            multi_select=True,
        )
        if directories:
            print(f"Selected {len(directories)} director(ies):")
            for directory in directories:
                print(f"  - {directory}")

    def example_file_dialog_class(self) -> None:
        """Example: Using FileDialog class for more control."""
        dialog = FileDialog(
            parent=self,
            title="Select Image File",
            file_filter="Images (*.png *.jpg *.jpeg *.bmp);;All Files (*.*)",
        )

        # Use the dialog instance
        files = dialog.open_file()
        if files:
            print(f"Selected image: {files[0]}")


if __name__ == "__main__":
    app = QApplication(sys.argv)

    demo = FileDialogDemo()
    demo.show()

    sys.exit(app.exec())
