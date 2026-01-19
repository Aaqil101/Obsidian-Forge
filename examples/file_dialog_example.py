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
from PySide6.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QFileDialog,
    QListView,
    QTreeView,
    QWidget,
)

# ----- UI Modules-----
from src.ui.styles import QFileDialog as QFileDialogStyle

# ----- Utils Modules-----
from src.utils import get_icon


class FileDialogDemo:
    """Demo window showing various file dialog configurations."""

    def __init__(self) -> None:
        # Multi folder selection
        self.show_multi_folder_dialog()

    def style_file_dialog(self, dialog: QFileDialog) -> None:
        """Apply custom styling and icons to the file dialog.

        Args:
            dialog: QFileDialog instance to style
        """
        # Customize toolbar buttons with SVG icons
        for tool_button in dialog.findChildren(QWidget):
            if isinstance(tool_button, QWidget):
                button_name: str = tool_button.objectName()

                # Back button
                if "backButton" in button_name or "Back" in button_name:
                    icon = get_icon("navigate_back.svg", color="#7aa2f7")
                    if hasattr(tool_button, "setIcon"):
                        tool_button.setIcon(icon)
                        tool_button.setToolTip("Back")

                # Forward button
                elif "forwardButton" in button_name or "Forward" in button_name:
                    icon = get_icon("navigate_forward.svg", color="#7aa2f7")
                    if hasattr(tool_button, "setIcon"):
                        tool_button.setIcon(icon)
                        tool_button.setToolTip("Forward")

                # Parent Directory / Up button
                elif (
                    "toParentButton" in button_name
                    or "Parent" in button_name
                    or "Up" in button_name
                ):
                    icon = get_icon("up_arrow.svg", color="#7aa2f7")
                    if hasattr(tool_button, "setIcon"):
                        tool_button.setIcon(icon)
                        tool_button.setToolTip("Parent Directory")

                # New Folder button
                elif "newFolderButton" in button_name or "NewFolder" in button_name:
                    icon = get_icon("folder_add.svg", color="#9ece6a")
                    if hasattr(tool_button, "setIcon"):
                        tool_button.setIcon(icon)
                        tool_button.setToolTip("New Folder")

                # List Mode button
                elif "listModeButton" in button_name or "List" in button_name:
                    icon = get_icon("list_view.svg", color="#7aa2f7")
                    if hasattr(tool_button, "setIcon"):
                        tool_button.setIcon(icon)
                        tool_button.setToolTip("List View")

                # Detail Mode button
                elif "detailModeButton" in button_name or "Detail" in button_name:
                    icon = get_icon("grid_view.svg", color="#7aa2f7")
                    if hasattr(tool_button, "setIcon"):
                        tool_button.setIcon(icon)
                        tool_button.setToolTip("Detail View")

    def show_multi_folder_dialog(self):
        """Show a multi-folder selection dialog."""
        dialog = QFileDialog()
        dialog.setFixedSize(900, 600)
        dialog.setWindowTitle("Select Multiple Folders")
        dialog.setFileMode(QFileDialog.FileMode.Directory)
        dialog.setOption(QFileDialog.Option.DontUseNativeDialog, True)
        dialog.setOption(QFileDialog.Option.ShowDirsOnly, True)

        # Apply custom styling
        self.style_file_dialog(dialog)

        # Enable multi-selection
        list_view = dialog.findChild(QListView, "listView")
        if list_view:
            list_view.setSelectionMode(
                QAbstractItemView.SelectionMode.ExtendedSelection
            )

        tree_view = dialog.findChild(QTreeView)
        if tree_view:
            tree_view.setSelectionMode(
                QAbstractItemView.SelectionMode.ExtendedSelection
            )
            # Ensure the Name column is properly sized to show full text
            tree_view.setColumnWidth(0, 300)  # Name column - wider width
            tree_view.setWordWrap(True)

            # Configure header
            header = tree_view.header()
            if header:
                header.setStretchLastSection(False)
                header.setSectionResizeMode(0, header.ResizeMode.Interactive)

        # Connect accepted signal to quit the application
        dialog.accepted.connect(lambda: self.on_dialog_accepted(dialog))
        dialog.rejected.connect(QApplication.quit)

        dialog.show()

    def on_dialog_accepted(self, dialog) -> None:
        """Handle dialog acceptance."""
        selected = dialog.selectedFiles()
        if selected:
            print(f"Selected {len(selected)} folder(s):")
            for folder in selected:
                print(f"  - {folder}")
        QApplication.quit()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Apply Tokyo Night theme
    app.setStyleSheet(QFileDialogStyle.qss())

    demo = FileDialogDemo()

    sys.exit(app.exec())
