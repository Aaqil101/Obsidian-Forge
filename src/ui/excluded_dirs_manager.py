"""
Excluded Directories Manager Window for Obsidian Forge.
Provides a dedicated interface for managing directories to exclude from scans.
"""

# ----- Built-In Modules-----
from pathlib import Path

# ----- PySide6 Modules -----
from PySide6.QtCore import QSize, Qt, QTimer
from PySide6.QtGui import QCursor, QFont
from PySide6.QtWidgets import (
    QAbstractItemView,
    QDialog,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QListView,
    QListWidget,
    QListWidgetItem,
    QTreeView,
    QVBoxLayout,
    QWidget,
)

# ----- Core Modules -----
from src.core.config import FONT_FAMILY, FONT_SIZE_HEADER, FONT_SIZE_TEXT, Config

# ----- UI Component Imports -----
from src.ui import PopupIcon, PopupWindow

# ----- Utils Modules -----
from src.utils import (
    COLOR_DARK_BLUE,
    COLOR_ORANGE,
    THEME_BG_PRIMARY,
    THEME_TEXT_PRIMARY,
    THEME_TEXT_SECONDARY,
    HoverIconButton,
    Icons,
    get_icon,
)


class ExcludedDirsManager(QDialog):
    """Dedicated window for managing excluded directories for vault scans.

    Features:
    - Large, easy-to-read list of excluded directories
    - Add/Remove buttons with multi-selection support
    - Text input dialog for adding directory names
    - Save/Cancel buttons
    - Tokyo Night themed styling
    """

    def __init__(self, config: Config, parent=None) -> None:
        """Initialize the excluded directories manager window.

        Args:
            config: Configuration instance
            parent: Parent widget
        """
        super().__init__(parent)
        self.config = config
        self.original_excluded: list[str] = self.config.excluded_directories.copy()
        self._init_ui()
        self._load_excluded_dirs()

    def _init_ui(self) -> None:
        """Initialize the user interface."""
        self.setWindowTitle("Manage Excluded Directories")
        self.setFixedSize(700, 500)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.WindowStaysOnTopHint)
        self.setModal(True)

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(16)
        main_layout.setContentsMargins(24, 24, 24, 24)

        # Background styling
        self.setStyleSheet(
            f"""
            QDialog {{
                background-color: {THEME_BG_PRIMARY};
            }}
            """
        )

        # Header
        header = self._create_header()
        main_layout.addWidget(header)

        # Description
        desc = QLabel(
            "Add directories to exclude from vault scans.\n"
            "You can exclude by folder name (e.g., '.obsidian') or by full path (e.g., 'Zettelkasten/98 - Organize/Canvas')."
        )
        desc.setFont(QFont(FONT_FAMILY, FONT_SIZE_TEXT))
        desc.setStyleSheet(f"color: {THEME_TEXT_SECONDARY}; padding: 0 0 8px 0;")
        desc.setWordWrap(True)
        main_layout.addWidget(desc)

        # List section
        list_section = self._create_list_section()
        main_layout.addWidget(list_section, 1)  # Stretch to fill space

        # Button bar
        button_bar = self._create_button_bar()
        main_layout.addWidget(button_bar)

    def _create_header(self) -> QWidget:
        """Create the header section with icon and title.

        Returns:
            QWidget: Header widget
        """
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        # Icon
        icon_label = QLabel()
        icon_label.setPixmap(
            get_icon("exclude.svg", color=f"{COLOR_ORANGE}").pixmap(QSize(24, 24))
        )
        icon_label.setFixedSize(24, 24)
        layout.addWidget(icon_label)

        # Title
        title_label = QLabel("Excluded Directories")
        title_label.setFont(QFont(FONT_FAMILY, FONT_SIZE_HEADER, QFont.Weight.Bold))
        title_label.setStyleSheet(f"color: {THEME_TEXT_PRIMARY};")
        layout.addWidget(title_label)

        layout.addStretch()

        return widget

    def _create_list_section(self) -> QWidget:
        """Create the list section with add/remove buttons.

        Returns:
            QWidget: List section widget
        """
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # List widget
        self.list_widget = QListWidget()
        self.list_widget.setFont(QFont(FONT_FAMILY, FONT_SIZE_TEXT))
        self.list_widget.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        self.list_widget.setStyleSheet(
            f"""
            QListWidget {{
                background-color: rgba(255, 255, 255, 0.04);
                color: {THEME_TEXT_PRIMARY};
                border-radius: 6px;
                padding: 2px;
            }}
            QListWidget::item {{
                border-radius: 4px;
                padding: 0px;
                margin: 0px 0;
            }}
            QListWidget::item:selected {{
                color: {THEME_TEXT_PRIMARY};
                background-color: rgba(122, 162, 247, 0.3);
            }}
            QListWidget::item:hover {{
                color: {THEME_TEXT_PRIMARY};
                background-color: rgba(255, 255, 255, 0.06);
            }}
            QListWidget::item:selected:!active {{
                color: {THEME_TEXT_PRIMARY};
                background: rgba(255, 255, 255, 0.08);
            }}
            QListWidget:focus {{
                color: {THEME_TEXT_PRIMARY};
                background-color: rgba(255, 255, 255, 0.06);
                outline: none;
            }}
            """
        )
        layout.addWidget(self.list_widget)

        # Buttons row
        buttons_row = self._create_list_buttons()
        layout.addWidget(buttons_row)

        return widget

    def _create_list_buttons(self) -> QWidget:
        """Create add/remove buttons for the list.

        Returns:
            QWidget: Buttons row widget
        """
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        layout.addStretch()

        # Browse button
        browse_btn = HoverIconButton(
            normal_icon=Icons.FOLDER_OUTLINE,
            hover_icon=Icons.FOLDER,
            pressed_icon=Icons.FOLDER_OPEN,
            text="Browse",
        )
        browse_btn.setFont(QFont(FONT_FAMILY, FONT_SIZE_TEXT))
        browse_btn.setFixedHeight(32)
        browse_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        browse_btn.setToolTip("Select folders from file system (multi-select)")
        browse_btn.setStyleSheet(
            f"""
            QPushButton {{
                background-color: rgba(158, 206, 106, 0.2);
                color: #9ece6a;
                border-radius: 6px;
                padding: 6px 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: rgba(158, 206, 106, 0.3);
                border-bottom: 2px solid #9ece6a;
            }}
            QPushButton:pressed {{
                background-color: rgba(158, 206, 106, 0.4);
            }}
            QPushButton:focus {{
                background-color: rgba(158, 206, 106, 0.3);
                border-bottom: 2px solid #9ece6a;
                outline: none;
            }}
            """
        )
        browse_btn.clicked.connect(self._on_browse_clicked)
        layout.addWidget(browse_btn)

        # Remove button
        remove_btn = HoverIconButton(
            normal_icon=Icons.TRASH_OUTLINE,
            hover_icon=Icons.TRASH,
            pressed_icon=Icons.TRASH_OCT,
            text="Remove",
        )
        remove_btn.setFont(QFont(FONT_FAMILY, FONT_SIZE_TEXT))
        remove_btn.setFixedHeight(32)
        remove_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        remove_btn.setStyleSheet(
            f"""
            QPushButton {{
                background-color: rgba(247, 118, 142, 0.2);
                color: #f7768e;
                border-radius: 6px;
                padding: 6px 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: rgba(247, 118, 142, 0.3);
                border-bottom: 2px solid #f7768e;
            }}
            QPushButton:pressed {{
                background-color: rgba(247, 118, 142, 0.4);
            }}
            QPushButton:focus {{
                background-color: rgba(247, 118, 142, 0.3);
                border-bottom: 2px solid #f7768e;
                outline: none;
            }}
            """
        )
        remove_btn.clicked.connect(self._on_remove_clicked)
        layout.addWidget(remove_btn)

        return widget

    def _create_button_bar(self) -> QWidget:
        """Create the bottom button bar with Save/Cancel.

        Returns:
            QWidget: Button bar widget
        """
        bar = QWidget()
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        layout.addStretch()

        # Cancel button
        cancel_btn = HoverIconButton(
            normal_icon=Icons.CANCEL_OUTLINE,
            hover_icon=Icons.CANCEL,
            text="Cancel",
        )
        cancel_btn.setFont(QFont(FONT_FAMILY, FONT_SIZE_TEXT))
        cancel_btn.setFixedHeight(36)
        cancel_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        cancel_btn.setStyleSheet(
            f"""
            QPushButton {{
                background-color: rgba(255, 255, 255, 0.04);
                color: {THEME_TEXT_PRIMARY};
                border-radius: 6px;
                padding: 8px 20px;
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
            """
        )
        cancel_btn.clicked.connect(self._on_cancel_clicked)
        layout.addWidget(cancel_btn)

        # Save button
        save_btn = HoverIconButton(
            normal_icon=Icons.SAVE,
            hover_icon=Icons.CONTENT_SAVE,
            pressed_icon=Icons.CONTENT_SAVE_CHECK,
            text="Save",
        )
        save_btn.setFont(QFont(FONT_FAMILY, FONT_SIZE_TEXT))
        save_btn.setFixedHeight(36)
        save_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        save_btn.setStyleSheet(
            f"""
            QPushButton {{
                background-color: rgba(158, 206, 106, 0.2);
                color: #9ece6a;
                border-radius: 6px;
                padding: 8px 20px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: rgba(158, 206, 106, 0.3);
                border-bottom: 2px solid #9ece6a;
            }}
            QPushButton:pressed {{
                background-color: rgba(158, 206, 106, 0.4);
            }}
            QPushButton:focus {{
                background-color: rgba(158, 206, 106, 0.3);
                border-bottom: 2px solid #9ece6a;
                outline: none;
            }}
            """
        )
        save_btn.clicked.connect(self._on_save_clicked)
        layout.addWidget(save_btn)

        # Set Save as default button (Enter key)
        save_btn.setDefault(True)

        return bar

    def _load_excluded_dirs(self) -> None:
        """Load current excluded directories into the list widget."""
        self.list_widget.clear()
        excluded_dirs: list[str] = self.config.excluded_directories
        for dir_name in sorted(excluded_dirs):
            item = QListWidgetItem(dir_name)
            self.list_widget.addItem(item)

    def _style_file_dialog(self, dialog: QFileDialog) -> None:
        """Apply custom styling and icons to the file dialog.

        Args:
            dialog: QFileDialog instance to style
        """
        # Customize toolbar buttons with SVG icons
        # Find and style the navigation buttons
        for tool_button in dialog.findChildren(QWidget):
            # Style the toolbar buttons
            if isinstance(tool_button, QWidget):
                button_name = tool_button.objectName()

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

    def _on_browse_clicked(self) -> None:
        """Handle Browse button click - select folders from file system."""

        # Check if vault path is configured
        if not self.config.vault_path:
            popup = PopupWindow(
                message="Please configure your vault path in settings before adding exclusions.",
                title="Vault Not Configured",
                icon=PopupIcon.WARNING,
                info_popup=True,
                parent=self,
            )
            popup.exec()
            return

        # Create file dialog with multi-selection enabled
        dialog = QFileDialog(self)
        dialog.setFixedSize(900, 600)
        dialog.setWindowTitle("Select Folder(s) to Exclude")
        dialog.setFileMode(QFileDialog.FileMode.Directory)
        dialog.setOption(QFileDialog.Option.DontUseNativeDialog, True)
        dialog.setOption(QFileDialog.Option.ShowDirsOnly, True)

        dialog.setStyleSheet()

        # Apply Tokyo Night styling to match application theme
        self._style_file_dialog(dialog)

        # Set initial directory to vault path
        dialog.setDirectory(str(self.config.vault_path))

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

        if dialog.exec() == QFileDialog.DialogCode.Accepted:
            folders: list[str] = dialog.selectedFiles()

            # Get existing items
            existing_items: list[str] = [
                self.list_widget.item(i).text() for i in range(self.list_widget.count())
            ]

            # Track results
            added_count = 0
            duplicate_count = 0
            outside_vault_count = 0

            vault_root = Path(self.config.vault_path)

            for folder in folders:
                folder_path = Path(folder)

                # Check if folder is inside vault
                try:
                    relative_path: Path = folder_path.relative_to(vault_root)
                    # Convert to forward slashes for consistency
                    path_str: str = str(relative_path).replace("\\", "/")
                except ValueError:
                    # Folder is outside vault
                    outside_vault_count += 1
                    continue

                # Check if already exists
                if path_str in existing_items:
                    duplicate_count += 1
                    continue

                # Add to list widget
                item = QListWidgetItem(path_str)
                self.list_widget.addItem(item)
                existing_items.append(path_str)
                added_count += 1

            # Sort items
            self.list_widget.sortItems()

            # Show summary
            messages = []
            if added_count > 0:
                msg: str = f"Added {added_count} director"
                msg += "ies" if added_count > 1 else "y"
                messages.append(msg)

            if duplicate_count > 0:
                messages.append(
                    f"{duplicate_count} duplicate{'s' if duplicate_count > 1 else ''} skipped"
                )

            if outside_vault_count > 0:
                messages.append(
                    f"{outside_vault_count} folder{'s' if outside_vault_count > 1 else ''} outside vault skipped"
                )

            if messages:
                popup = PopupWindow(
                    message="\n".join(messages),
                    title="Folders Added",
                    icon=PopupIcon.SUCCESS if added_count > 0 else PopupIcon.INFO,
                    info_popup=True,
                    parent=self,
                )
                popup.exec()

    def _on_remove_clicked(self) -> None:
        """Handle Remove button click."""
        selected_items = self.list_widget.selectedItems()
        if not selected_items:
            popup = PopupWindow(
                message="Please select one or more directories to remove.",
                title="No Selection",
                icon=PopupIcon.INFO,
                info_popup=True,
                parent=self,
            )
            popup.exec()
            return

        # Confirm removal
        count: int = len(selected_items)
        dir_text = "directory" if count == 1 else "directories"
        popup = PopupWindow(
            message=f"Remove {count} excluded {dir_text}?",
            title="Confirm Removal",
            icon=PopupIcon.WARNING,
            buttons=["Yes", "No"],
            parent=self,
        )

        if popup.exec() == QDialog.DialogCode.Accepted:
            # Remove items in reverse order to avoid index issues
            for item in selected_items:
                self.list_widget.takeItem(self.list_widget.row(item))

    def _on_save_clicked(self) -> None:
        """Handle Save button click."""
        # Get all items from list
        excluded_dirs: list[str] = [
            self.list_widget.item(i).text() for i in range(self.list_widget.count())
        ]

        # Ensure we have at least the defaults if list is empty
        if not excluded_dirs:
            excluded_dirs = [".obsidian", ".space", ".trash"]

        # Save to config
        self.config.excluded_directories = excluded_dirs

        if self.config.save_settings():
            # Show success popup
            popup = PopupWindow(
                message="Excluded directories saved successfully.",
                title="Settings Saved",
                icon=PopupIcon.SUCCESS,
                info_popup=True,
                parent=self,
            )
            popup.show()

            # Auto-close popup after 500 millisecond, then close the manager window
            QTimer.singleShot(500, lambda: (popup.accept(), self.accept()))
        else:
            popup = PopupWindow(
                message="Failed to save excluded directories. Please try again.",
                title="Save Failed",
                icon=PopupIcon.ERROR,
                info_popup=True,
                parent=self,
            )
            popup.exec()

    def _on_cancel_clicked(self) -> None:
        """Handle Cancel button click."""
        # Check if changes were made
        current_dirs: list[str] = [
            self.list_widget.item(i).text() for i in range(self.list_widget.count())
        ]

        if set(current_dirs) != set(self.original_excluded):
            popup = PopupWindow(
                message="You have unsaved changes. Discard them?",
                title="Unsaved Changes",
                icon=PopupIcon.WARNING,
                buttons=["Yes", "No"],
                parent=self,
            )
            if popup.exec() != QDialog.DialogCode.Accepted:
                return

        self.reject()
