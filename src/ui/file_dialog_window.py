"""
Reusable file dialog component for Obsidian Forge.
"""

# ----- Built-In Modules-----
from typing import List

# ----- PySide6 Modules -----
from PySide6.QtWidgets import (
    QAbstractItemView,
    QFileDialog,
    QListView,
    QTreeView,
    QWidget,
)

# ----- Core Modules-----
from src.core import BORDER_RADIUS_SMALL

# ----- Utils Modules -----
from src.utils import COLOR_DARK_BLUE, THEME_BG_PRIMARY, THEME_TEXT_PRIMARY, get_icon


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
        dialog.setOptions(
            QFileDialog.Option.DontUseNativeDialog
            | QFileDialog.Option.HideNameFilterDetails
            | QFileDialog.Option.DontUseCustomDirectoryIcons
        )

        if self.directory:
            dialog.setDirectory(self.directory)

        if self.file_filter:
            dialog.setNameFilter(self.file_filter)

        # Apply custom styling
        dialog.setStyleSheet(
            f"""
            /* === Main Dialog === */
            QFileDialog {{
                background-color: {THEME_BG_PRIMARY};
                color: {THEME_TEXT_PRIMARY};
            }}

            /* === Tree View === */
            QTreeView {{
                background-color: #282828;
                color: {THEME_TEXT_PRIMARY};
                border: 1px solid #444444;
                outline: 0;
            }}
            QTreeView::item {{
                color: {THEME_TEXT_PRIMARY};
                padding: 0px 2px;
                min-height: 14px;
            }}
            QTreeView::item:hover {{
                color: {THEME_TEXT_PRIMARY};
                background-color: #4F4F4F;
            }}
            QTreeView::item:selected {{
                color: {THEME_TEXT_PRIMARY};
                background-color: #3B5689;
            }}
            QTreeView::item:selected:!active {{
                color: {THEME_TEXT_PRIMARY};
            }}

            /* === List View === */
            QListView {{
                background-color: #282828;
                color: {THEME_TEXT_PRIMARY};
                border: 1px solid #444444;
                outline: 0;
            }}
            QListView::item {{
                color: {THEME_TEXT_PRIMARY};
                padding: 0px 2px;
                height: 28px;
            }}
            QListView::item:hover {{
                background-color: #4F4F4F;
            }}
            QListView::item:selected {{
                background-color: #3B5689;
            }}
            QListView::item:selected:!active {{
                color: {THEME_TEXT_PRIMARY};
            }}

            /* === Menu === */
            QMenu {{
                background-color: #1F1F1F;
                color: {THEME_TEXT_PRIMARY};
                border: 1px solid #323232;
                border-radius: 0px;
                padding: 0px;
            }}
            QMenu::item {{
                color: {THEME_TEXT_PRIMARY};
                border-radius: 0px;
                padding: 2px 8px;
                min-height: 16px;
            }}
            QMenu::item::selected {{
                color: {THEME_TEXT_PRIMARY};
                background-color: #5076B2;
                border-radius: 0px;
            }}
            QMenu::icon {{
                margin: 3px;
            }}
            QMenu::item:disabled {{
                color: #828282;
            }}
            QMenu::separator {{
                background-color: #616161;
                border: none;
                height: 1px;
                margin: 0px 4px 0px 4px;
            }}

            /* === Header View === */
            QHeaderView {{
                background-color: #282828;
                color: {THEME_TEXT_PRIMARY};
            }}
            QHeaderView::section {{
                background-color: rgba(255, 255, 255, 0.04);
                border: 0.5px solid rgba(255, 255, 255, 0.08);
                text-align: center;
                padding: 2px 4px;
                min-height: 18px;
            }}

            /* === Splitter === */
            QSplitter::handle {{
                background-color: #444444;
                width: 3px;
                height: 3px;
            }}

            /* === ComboBox === */
            QComboBox {{
                background-color: #1F1F1F;
                color: {THEME_TEXT_PRIMARY};
                border: 1px solid #444444;
                border-radius: 0px;
                padding: 1px 1px 1px 3px;
            }}
            QComboBox:hover {{
                background-color: rgba(255, 255, 255, 0.06);
            }}
            QComboBox:focus {{
                background-color: rgba(255, 255, 255, 0.06);
                outline: none;
            }}
            QComboBox::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border: none;
                background: transparent;
            }}
            QComboBox::down-arrow {{
                image: url(:/assets/expand_more.svg);
                width: 10px;
                height: 10px;
                border: none;
            }}
            QComboBox::down-arrow:on {{
                image: url(:/assets/expand_less.svg);
            }}

            /* Dropdown list styling */
            QComboBox QAbstractItemView {{
                background-color: {THEME_BG_PRIMARY};
                color: {THEME_TEXT_PRIMARY};
                border-radius: 4px;
                selection-background-color: {COLOR_DARK_BLUE};
                selection-color: {THEME_TEXT_PRIMARY};
                show-decoration-selected: 1;
                outline: none;
            }}
            QComboBox QAbstractItemView::item {{
                background-color: {THEME_BG_PRIMARY};
                color: {THEME_TEXT_PRIMARY};
                min-height: 18px;
                padding: 2px 4px;
                border: none;
            }}
            QComboBox QAbstractItemView::item:hover {{
                background-color: rgba(83, 144, 247, 0.25);
                color: {THEME_TEXT_PRIMARY};
            }}
            QComboBox QAbstractItemView::item:selected {{
                background-color: rgba(83, 144, 247, 0.25);
                color: {THEME_TEXT_PRIMARY};
            }}
            QComboBox QAbstractItemView::item:selected:hover {{
                background-color: rgba(83, 144, 247, 0.25);
                border: none;
            }}

            /* === Labels === */
            QLabel {{
                background-color: transparent;
                color: "#FFFFFF";
            }}

            /* === Line Edit === */
            QLineEdit {{
                background-color: #1F1F1F;
                color: {THEME_TEXT_PRIMARY};
                border: 1px solid #444444;
                border-radius: 0px;
                padding: 1px;
            }}
            QLineEdit[text=\"\"] {{
                color: {THEME_TEXT_PRIMARY};
            }}

            /* === Buttons === */
            QPushButton {{
                background-color: rgba(255, 255, 255, 0.04);
                color: {THEME_TEXT_PRIMARY};
                border-radius: 0px;
                padding: 3px 10px;
                min-height: 18px;
            }}
            QPushButton:hover {{
                background-color: rgba(255, 255, 255, 0.08);
                border-bottom: 2px solid {COLOR_DARK_BLUE};
            }}
            QPushButton:pressed {{
                background-color: rgba(255, 255, 255, 0.12);
            }}
            QPushButton:focus {{
                background-color: rgba(255, 255, 255, 0.08);
                border-bottom: 2px solid {COLOR_DARK_BLUE};
                outline: none;
            }}

            /* === Tool Button === */
            QToolButton {{
                background-color: rgba(255, 255, 255, 0.04);
                border: none;
                border-radius: {BORDER_RADIUS_SMALL}px;
                padding: 2px;
                min-width: 20px;
                min-height: 20px;
            }}
            QToolButton:hover {{
                background-color: rgba(122, 162, 247, 0.15);
            }}
            QToolButton:pressed {{
                background-color: rgba(122, 162, 247, 0.25);
            }}
            """
        )
        self._style_dialog(dialog)

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
            tree_view.setColumnWidth(0, 300)  # Name column width
            tree_view.setWordWrap(True)

            # Configure header
            header = tree_view.header()
            if header:
                header.setStretchLastSection(False)
                header.setSectionResizeMode(0, header.ResizeMode.Interactive)

    def open_file(self, multi_select: bool = False) -> list[str] | None:
        """
        Open a file selection dialog.

        Args:
            multi_select: Allow multiple file selection if True

        Returns:
            List of selected file paths, or None if cancelled
        """
        dialog = self._create_dialog()

        if multi_select:
            dialog.setFileMode(QFileDialog.FileMode.ExistingFiles)
        else:
            dialog.setFileMode(QFileDialog.FileMode.ExistingFile)

        self._configure_views(dialog, multi_select)

        if dialog.exec():
            return dialog.selectedFiles()
        return None

    def save_file(self, default_name: str = "") -> str | None:
        """
        Open a file save dialog.

        Args:
            default_name: Default filename to suggest

        Returns:
            Selected file path, or None if cancelled
        """
        dialog = self._create_dialog()
        dialog.setFileMode(QFileDialog.FileMode.AnyFile)
        dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)

        if default_name:
            dialog.selectFile(default_name)

        self._configure_views(dialog, False)

        if dialog.exec():
            files: List[str] = dialog.selectedFiles()
            return files[0] if files else None
        return None

    def select_directory(self, multi_select: bool = False) -> list[str] | None:
        """
        Open a directory selection dialog.

        Args:
            multi_select: Allow multiple directory selection if True

        Returns:
            List of selected directory paths, or None if cancelled
        """
        dialog = self._create_dialog()
        dialog.setFileMode(QFileDialog.FileMode.Directory)
        dialog.setOption(QFileDialog.Option.ShowDirsOnly)

        self._configure_views(dialog, multi_select)

        if dialog.exec():
            return dialog.selectedFiles()
        return None


# Convenience functions for quick usage
def open_file_dialog(
    parent: QWidget | None = None,
    title: str = "Open File",
    directory: str = "",
    file_filter: str = "All Files (*.*)",
    multi_select: bool = False,
) -> list[str] | None:
    """
    Quick function to open a file selection dialog.

    Args:
        parent: Parent widget
        title: Dialog title
        directory: Initial directory
        file_filter: File type filter
        multi_select: Allow multiple selection

    Returns:
        List of selected file paths, or None if cancelled
    """
    dialog = FileDialog(parent, title, directory, file_filter)
    return dialog.open_file(multi_select)


def save_file_dialog(
    parent: QWidget | None = None,
    title: str = "Save File",
    directory: str = "",
    file_filter: str = "All Files (*.*)",
    default_name: str = "",
) -> str | None:
    """
    Quick function to open a file save dialog.

    Args:
        parent: Parent widget
        title: Dialog title
        directory: Initial directory
        file_filter: File type filter
        default_name: Default filename

    Returns:
        Selected file path, or None if cancelled
    """
    dialog = FileDialog(parent, title, directory, file_filter)
    return dialog.save_file(default_name)


def select_directory_dialog(
    parent: QWidget | None = None,
    title: str = "Select Directory",
    directory: str = "",
    multi_select: bool = False,
) -> list[str] | None:
    """
    Quick function to open a directory selection dialog.

    Args:
        parent: Parent widget
        title: Dialog title
        directory: Initial directory
        multi_select: Allow multiple selection

    Returns:
        List of selected directory paths, or None if cancelled
    """
    dialog = FileDialog(parent, title, directory)
    return dialog.select_directory(multi_select)
