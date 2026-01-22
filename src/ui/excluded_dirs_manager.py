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
    QDialog,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QVBoxLayout,
    QWidget,
)

# ----- Core Modules -----
from src.core.config import FONT_FAMILY, FONT_SIZE_HEADER, FONT_SIZE_TEXT, Config

# ----- UI Component Imports -----
from src.ui import FileDialog, PopupIcon, PopupWindow

# ----- Utils Modules -----
from src.utils import (
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
        self.setMinimumSize(600, 540)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.WindowStaysOnTopHint)
        self.setModal(True)

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(8)
        main_layout.setContentsMargins(12, 12, 12, 12)

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
        main_layout.addWidget(list_section)

        # Button bar
        button_bar = self._create_button_bar()
        button_bar.setContentsMargins(0, 0, 0, 0)
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
        layout.setSpacing(0)

        # List widget
        self.list_widget = QListWidget()
        self.list_widget.setFont(QFont(FONT_FAMILY, FONT_SIZE_TEXT))
        self.list_widget.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)

        layout.addWidget(self.list_widget)

        return widget

    def _create_button_bar(self) -> QWidget:
        """Create the bottom button bar with all buttons.

        Returns:
            QWidget: Button bar widget
        """
        bar = QWidget()
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        layout.addStretch()

        # Cancel button
        cancel_btn = HoverIconButton(
            normal_icon=Icons.CANCEL_OUTLINE,
            hover_icon=Icons.CANCEL,
            text="Cancel",
        )
        cancel_btn.setFont(QFont(FONT_FAMILY, FONT_SIZE_TEXT))
        cancel_btn.setProperty("CancelButton", True)
        cancel_btn.setFixedHeight(30)
        cancel_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        cancel_btn.clicked.connect(self._on_cancel_clicked)
        layout.addWidget(cancel_btn)

        # Browse button
        browse_btn = HoverIconButton(
            normal_icon=Icons.FOLDER_OUTLINE,
            hover_icon=Icons.FOLDER,
            pressed_icon=Icons.FOLDER_OPEN,
            text="Browse",
        )
        browse_btn.setFont(QFont(FONT_FAMILY, FONT_SIZE_TEXT))
        browse_btn.setProperty("BrowseButton", True)
        browse_btn.setFixedHeight(30)
        browse_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        browse_btn.setToolTip("Select folders from file system (multi-select)")
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
        remove_btn.setProperty("RemoveButton", True)
        remove_btn.setFixedHeight(30)
        remove_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        remove_btn.setToolTip("Remove selected directories from the list")
        remove_btn.clicked.connect(self._on_remove_clicked)
        layout.addWidget(remove_btn)

        # Save button
        save_btn = HoverIconButton(
            normal_icon=Icons.SAVE,
            hover_icon=Icons.CONTENT_SAVE,
            pressed_icon=Icons.CONTENT_SAVE_CHECK,
            text="Save",
        )
        save_btn.setFont(QFont(FONT_FAMILY, FONT_SIZE_TEXT))
        save_btn.setFixedHeight(30)
        save_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        save_btn.setProperty("SaveButton", True)

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

        # Use the FileDialog component
        dialog = FileDialog(
            parent=self,
            title="Select Folder(s) to Exclude",
            directory=str(self.config.vault_path),
        )
        folders = dialog.get_directory(
            multi_select=True,
        )

        if folders:

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

            # Auto-close popup after 1 second, then close the manager window
            QTimer.singleShot(1000, lambda: (popup.accept(), self.accept()))
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
