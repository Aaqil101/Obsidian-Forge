"""
Reusable file dialog component for Obsidian Forge.
"""

# ----- PySide6 Modules -----
from PySide6.QtWidgets import (
    QAbstractItemView,
    QFileDialog,
    QListView,
    QTreeView,
    QWidget,
)

# ----- Utils Modules -----
from src.utils import get_icon


class FileDialog:
    """
    Reusable file dialog with Tokyo Night styling and custom icons.

    This class provides a consistent file dialog interface across the application
    with pre-configured styling and icon customization.
    """

    def __init__(
        self,
        parent: QWidget | None = None,
        title: str = "Select File",
        directory: str = "",
        file_filter: str = "All Files (*.*)",
    ) -> None:
        """
        Initialize the file dialog.

        Args:
            parent: Parent widget (optional)
            title: Dialog window title
            directory: Initial directory to open
            file_filter: File type filter string (e.g., "Images (*.png *.jpg);;All Files (*.*)")
        """
        self.parent = parent
        self.title: str = title
        self.directory: str = directory
        self.file_filter: str = file_filter
        self._dialog: QFileDialog | None = None

    def _create_dialog(self) -> QFileDialog:
        """Create and configure the base file dialog."""
        dialog = QFileDialog(self.parent)
        dialog.setMinimumSize(900, 600)
        dialog.setWindowTitle(self.title)

        if self.directory:
            dialog.setDirectory(self.directory)

        if self.file_filter:
            dialog.setNameFilter(self.file_filter)

        return dialog

    def _style_dialog(self, dialog: QFileDialog) -> None:
        """Apply custom styling and icons to the file dialog.

        Args:
            dialog: QFileDialog instance to style
        """
        # Customize toolbar buttons with SVG icons
        for widget in dialog.findChildren(QWidget):
            if not isinstance(widget, QWidget):
                continue

            button_name: str = widget.objectName()

            # Back button
            if "backButton" in button_name or "Back" in button_name:
                icon = get_icon("navigate_back.svg", color="#7aa2f7")
                if hasattr(widget, "setIcon"):
                    widget.setIcon(icon)
                    widget.setToolTip("Back")

            # Forward button
            elif "forwardButton" in button_name or "Forward" in button_name:
                icon = get_icon("navigate_forward.svg", color="#7aa2f7")
                if hasattr(widget, "setIcon"):
                    widget.setIcon(icon)
                    widget.setToolTip("Forward")

            # Parent Directory / Up button
            elif (
                "toParentButton" in button_name
                or "Parent" in button_name
                or "Up" in button_name
            ):
                icon = get_icon("up_arrow.svg", color="#7aa2f7")
                if hasattr(widget, "setIcon"):
                    widget.setIcon(icon)
                    widget.setToolTip("Parent Directory")

            # New Folder button
            elif "newFolderButton" in button_name or "NewFolder" in button_name:
                icon = get_icon("folder_add.svg", color="#9ece6a")
                if hasattr(widget, "setIcon"):
                    widget.setIcon(icon)
                    widget.setToolTip("New Folder")

            # List Mode button
            elif "listModeButton" in button_name or "List" in button_name:
                icon = get_icon("list_view.svg", color="#7aa2f7")
                if hasattr(widget, "setIcon"):
                    widget.setIcon(icon)
                    widget.setToolTip("List View")

            # Detail Mode button
            elif "detailModeButton" in button_name or "Detail" in button_name:
                icon = get_icon("grid_view.svg", color="#7aa2f7")
                if hasattr(widget, "setIcon"):
                    widget.setIcon(icon)
                    widget.setToolTip("Detail View")

    def _configure_views(self, dialog: QFileDialog, multi_select: bool = False) -> None:
        """Configure list and tree views for the dialog.

        Args:
            dialog: QFileDialog instance to configure
            multi_select: Enable multi-selection if True
        """
        selection_mode = (
            QAbstractItemView.SelectionMode.ExtendedSelection
            if multi_select
            else QAbstractItemView.SelectionMode.SingleSelection
        )

        # Configure list view
        list_view = dialog.findChild(QListView, "listView")
        if list_view:
            list_view.setSelectionMode(selection_mode)
            list_view.setMinimumWidth(200)  # Set minimum width for sidebar
            list_view.setMaximumWidth(300)  # Set maximum width for sidebar

        # Configure tree view
        tree_view = dialog.findChild(QTreeView)
        if tree_view:
            tree_view.setSelectionMode(selection_mode)
            tree_view.setColumnWidth(0, 350)  # Name column width
            tree_view.setWordWrap(True)

            # Configure header
            header = tree_view.header()
            if header:
                header.setStretchLastSection(False)
                header.setSectionResizeMode(0, header.ResizeMode.Interactive)

    def get_directory(self, multi_select: bool = False) -> list[str] | None:
        """
        Open a directory selection dialog.

        Args:
            multi_select: Allow multiple directory selection if True

        Returns:
            List of selected directory paths, or None if cancelled
        """
        dialog = self._create_dialog()
        dialog.setOptions(
            QFileDialog.DontUseNativeDialog
            | QFileDialog.ShowDirsOnly
            | QFileDialog.HideNameFilterDetails
            | QFileDialog.DontUseCustomDirectoryIcons
        )
        dialog.setFileMode(QFileDialog.FileMode.Directory)

        self._configure_views(dialog, multi_select)
        self._style_dialog(dialog)

        if dialog.exec():
            return dialog.selectedFiles()
        return None
