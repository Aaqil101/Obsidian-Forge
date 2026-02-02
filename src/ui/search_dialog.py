"""
Script search dialog for quick access to scripts without opening main window.
Flow Launcher-style searchable list of all available scripts (daily + weekly).
"""

# ----- Built-In Modules -----
from dataclasses import dataclass

# ----- PySide6 Modules -----
from PySide6.QtCore import QEasingCurve, QPropertyAnimation, QSize, Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

# ----- Core Modules -----
from src.core import FONT_FAMILY, ScriptExecutor

# ----- Utils Modules -----
from src.utils import get_icon


@dataclass
class ScriptSearchItem:
    """Data class for script search items."""

    name: str
    path: str
    icon: str
    script_type: str  # 'daily', 'weekly', or 'system'
    display_text: str  # "Win [D]" or "Progress [W]"
    is_system_action: bool = False  # True for system actions like restart


class ScriptItemWidget(QWidget):
    """Custom widget for displaying script items with title and subtitle."""

    def __init__(self, script: ScriptSearchItem, parent=None) -> None:
        super().__init__(parent)
        self.script = script

        # Main horizontal layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(10)

        # Icon label
        icon_label = QLabel()
        try:
            if script.icon:
                icon = get_icon(script.icon)
            else:
                icon = get_icon("file.svg")
            icon_label.setPixmap(icon.pixmap(QSize(32, 32)))
        except Exception:
            pass
        icon_label.setFixedSize(32, 32)
        layout.addWidget(icon_label)

        # Text layout (vertical: title + subtitle)
        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)
        text_layout.setContentsMargins(0, 0, 0, 0)

        # Title
        title_label = QLabel(script.name)
        title_label.setFont(QFont(FONT_FAMILY, 11))
        title_label.setProperty("Title", True)
        text_layout.addWidget(title_label)

        # Subtitle (script type and path)
        if script.is_system_action:
            subtitle_text = "System action"
        else:
            subtitle_text = (
                f"{'Daily' if script.script_type == 'daily' else 'Weekly'} script"
            )
        subtitle_label = QLabel(subtitle_text)
        subtitle_label.setProperty("Subtitle", True)
        subtitle_label.setFont(QFont(FONT_FAMILY, 9))

        text_layout.addWidget(subtitle_label)

        layout.addLayout(text_layout)

        # Spacer to push badge to the right
        layout.addStretch()

        # Badge for script type (only for scripts, not system actions)
        if not script.is_system_action:
            badge_label = QLabel("[D]" if script.script_type == "daily" else "[W]")
            badge_label.setProperty("Badge", True)
            badge_label.setFont(QFont(FONT_FAMILY, 9))

            layout.addWidget(badge_label)


class ScriptSearchDialog(QDialog):
    """
    Floating search dialog for quick script access from system tray.

    Provides a searchable list of all scripts with keyboard shortcuts:
    - Type to filter scripts
    - /D prefix: filter to daily scripts only
    - /W prefix: filter to weekly scripts only
    - Enter: execute selected/first visible script
    - Escape: close dialog
    - Arrow keys: navigate list

    Signals:
        script_selected: Emitted with (script_name, script_path) when script is chosen
        restart_requested: Emitted when user wants to restart the application
    """

    script_selected = Signal(str, str)  # (script_name, script_path)
    frontmatter_edit_requested = Signal(str)  # Request frontmatter editor with note_type
    restart_requested = Signal()  # Request application restart
    exit_requested = Signal()  # Request application exit

    def __init__(self, executor: ScriptExecutor, parent=None) -> None:
        """
        Initialize the script search dialog.

        Args:
            executor: ScriptExecutor instance for loading available scripts
            parent: Parent widget (optional)
        """
        super().__init__(parent)
        self.executor = executor
        self.all_scripts: list[ScriptSearchItem] = []

        # Window configuration - frameless, transparent, always on top
        # Using Popup instead of Tool for better focus behavior
        self.setWindowFlags(
            Qt.WindowType.Popup
            | Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.NoDropShadowWindowHint
        )
        self.setWindowTitle("Obsidian Forge")
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedWidth(650)

        # Setup fade animations
        self._setup_animations()

        self._setup_ui()
        self._load_scripts()

    def _setup_animations(self) -> None:
        """Setup fade in/out animations for the dialog."""
        # Fade in animation
        self.fade_in = QPropertyAnimation(self, b"windowOpacity")
        self.fade_in.setDuration(150)  # 150ms fade in
        self.fade_in.setStartValue(0.0)
        self.fade_in.setEndValue(1.0)
        self.fade_in.setEasingCurve(QEasingCurve.Type.OutCubic)

        # Fade out animation
        self.fade_out = QPropertyAnimation(self, b"windowOpacity")
        self.fade_out.setDuration(100)  # 100ms fade out
        self.fade_out.setStartValue(1.0)
        self.fade_out.setEndValue(0.0)
        self.fade_out.setEasingCurve(QEasingCurve.Type.InCubic)
        # Hide the dialog when fade out completes
        self.fade_out.finished.connect(lambda: super(ScriptSearchDialog, self).hide())

    def hide_animated(self) -> None:
        """Hide the dialog with fade out animation."""
        if self.isVisible():
            self.fade_out.start()

    def _setup_ui(self) -> None:
        """Setup the dialog UI - Flow Launcher style."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(0)

        # Container widget for unified appearance
        self.container = QWidget()
        self.container.setObjectName("SearchContainer")
        self.container.setSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum
        )
        container_layout = QVBoxLayout(self.container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)
        container_layout.setSizeConstraint(
            QVBoxLayout.SizeConstraint.SetDefaultConstraint
        )

        # Search input with icon on right (Spotlight style)
        self.search_input = QLineEdit()
        self.search_input.setProperty("SearchBar", True)
        self.search_input.setPlaceholderText("Search scripts...")
        self.search_input.setFont(QFont(FONT_FAMILY, 13))
        self.search_input.setMinimumHeight(40)
        self.search_input.setMaximumHeight(40)
        self.search_input.textChanged.connect(self._filter_scripts)
        # Search icon on the right side (trailing position)
        self.search_input.addAction(
            get_icon("search.svg"),
            QLineEdit.ActionPosition.TrailingPosition,
        )
        container_layout.addWidget(self.search_input)

        # Script list with larger items (initially hidden)
        self.script_list = QListWidget()
        self.script_list.setProperty("ScriptList", True)
        self.script_list.setFont(QFont(FONT_FAMILY, 11))
        self.script_list.setIconSize(QSize(32, 32))
        self.script_list.setSpacing(4)
        self.script_list.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.script_list.setSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum
        )
        self.script_list.itemClicked.connect(self._on_item_clicked)
        self.script_list.itemActivated.connect(self._on_item_activated)
        self.script_list.setMaximumHeight(0)  # Start with 0 height
        self.script_list.setMinimumHeight(0)
        self.script_list.hide()  # Start hidden
        container_layout.addWidget(self.script_list)

        main_layout.addWidget(self.container)

    def _load_scripts(self) -> None:
        """Load all scripts (daily + weekly) from the executor into memory only."""
        self.all_scripts.clear()

        # Add system actions first
        daily_frontmatter_item = ScriptSearchItem(
            name="Edit Daily Frontmatter",
            path="daily",  # Store note_type in path field for system actions
            icon="edit.svg",
            script_type="system",
            display_text="Edit Daily Frontmatter",
            is_system_action=True,
        )
        self.all_scripts.append(daily_frontmatter_item)

        weekly_frontmatter_item = ScriptSearchItem(
            name="Edit Weekly Frontmatter",
            path="weekly",  # Store note_type in path field for system actions
            icon="edit.svg",
            script_type="system",
            display_text="Edit Weekly Frontmatter",
            is_system_action=True,
        )
        self.all_scripts.append(weekly_frontmatter_item)

        restart_item = ScriptSearchItem(
            name="Restart Application",
            path="",
            icon="refresh.svg",
            script_type="system",
            display_text="Restart Application",
            is_system_action=True,
        )
        self.all_scripts.append(restart_item)

        exit_item = ScriptSearchItem(
            name="Exit Application",
            path="",
            icon="exit.svg",
            script_type="system",
            display_text="Exit Application",
            is_system_action=True,
        )
        self.all_scripts.append(exit_item)

        # Load daily scripts
        daily_scripts = self.executor.get_available_scripts("daily")
        for script in daily_scripts:
            item = ScriptSearchItem(
                name=script["name"],
                path=script["path"],
                icon=script["icon"],
                script_type="daily",
                display_text=f"{script['name']} [D]",
            )
            self.all_scripts.append(item)

        # Load weekly scripts
        weekly_scripts = self.executor.get_available_scripts("weekly")
        for script in weekly_scripts:
            item = ScriptSearchItem(
                name=script["name"],
                path=script["path"],
                icon=script["icon"],
                script_type="weekly",
                display_text=f"{script['name']} [W]",
            )
            self.all_scripts.append(item)

    def _add_list_item(self, script: ScriptSearchItem) -> None:
        """
        Add a script item to the list widget with custom widget.

        Args:
            script: ScriptSearchItem to add to the list
        """
        item = QListWidgetItem()

        # Store script data with the item for later retrieval
        item.setData(Qt.ItemDataRole.UserRole, script)

        # Create custom widget for the item
        widget = ScriptItemWidget(script)

        # Set item height (width will auto-fit to list widget)
        item.setSizeHint(QSize(0, 44))

        # Add item and set custom widget
        self.script_list.addItem(item)
        self.script_list.setItemWidget(item, widget)

    def _filter_scripts(self, text: str) -> None:
        """
        Filter the script list based on search text.

        Supports filter prefixes:
        - /D or /d: Show only daily scripts
        - /W or /w: Show only weekly scripts

        Args:
            text: Search text from the input field
        """
        search_text = text.lower().strip()

        # Clear the list widget
        self.script_list.clear()

        # If search is empty, hide the list and resize window
        if not search_text:
            self.script_list.setMaximumHeight(0)
            self.script_list.setMinimumHeight(0)
            self.script_list.hide()
            self._resize_keeping_position()
            return

        # Check for filter prefix
        filter_type = None
        if search_text.startswith("/d"):
            filter_type = "daily"
            search_text: str = search_text[2:].strip()
        elif search_text.startswith("/w"):
            filter_type = "weekly"
            search_text = search_text[2:].strip()

        # Build filtered list
        visible_count = 0
        for script_data in self.all_scripts:
            # Type filter
            if filter_type:
                # For frontmatter edit actions, match them with their corresponding type
                if script_data.is_system_action:
                    if script_data.name == "Edit Daily Frontmatter" and filter_type != "daily":
                        continue
                    elif script_data.name == "Edit Weekly Frontmatter" and filter_type != "weekly":
                        continue
                    elif script_data.name not in ["Edit Daily Frontmatter", "Edit Weekly Frontmatter"]:
                        # Other system actions (restart, exit) are excluded when using filters
                        continue
                elif script_data.script_type != filter_type:
                    continue

            # Text filter (show all if search_text is empty after prefix removal)
            if search_text and search_text not in script_data.name.lower():
                continue

            # Add matching item to the list
            self._add_list_item(script_data)
            visible_count += 1

        # Show placeholder if no matches
        if visible_count == 0:
            placeholder_item = QListWidgetItem()
            placeholder_text = (
                "No matching scripts found"
                if self.all_scripts
                else "No scripts available"
            )
            placeholder_label = QLabel(placeholder_text)
            placeholder_label.setFont(QFont(FONT_FAMILY, 10))
            placeholder_label.setProperty("PlaceHolder", True)
            placeholder_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            placeholder_item.setSizeHint(QSize(0, 50))
            placeholder_item.setFlags(Qt.ItemFlag.NoItemFlags)
            self.script_list.addItem(placeholder_item)
            self.script_list.setItemWidget(placeholder_item, placeholder_label)

        # Show the list and resize window
        self.script_list.setMaximumHeight(16777215)  # Reset max height
        self.script_list.setMinimumHeight(0)  # Reset min height
        if visible_count == 0:
            # For placeholder, use exact height needed
            self.script_list.setFixedHeight(62)  # 50 (item) + 12 (padding)
        else:
            # For actual results, calculate based on visible count
            self.script_list.setFixedHeight(min(400, visible_count * 48 + 16))
        self.script_list.show()
        self._resize_keeping_position()

        # Auto-select first item if there are results
        if visible_count > 0:
            self.script_list.setCurrentRow(0)

    def _on_item_clicked(self, item: QListWidgetItem) -> None:
        """
        Handle single click on a list item.

        Args:
            item: The clicked list item
        """
        # Just select the item, don't execute yet
        # Execute on double-click or Enter key
        pass

    def _on_item_activated(self, item: QListWidgetItem) -> None:
        """
        Handle double-click or Enter on a list item.

        Args:
            item: The activated list item
        """
        self._execute_selected()

    def _execute_selected(self) -> None:
        """Execute the currently selected script or system action and close the dialog."""
        current = self.script_list.currentItem()
        if current:
            # Retrieve script data stored in the item
            script = current.data(Qt.ItemDataRole.UserRole)
            if script and isinstance(script, ScriptSearchItem):
                self.hide_animated()
                # Check if it's a system action
                if script.is_system_action:
                    if script.name == "Edit Daily Frontmatter":
                        self.frontmatter_edit_requested.emit("daily")
                    elif script.name == "Edit Weekly Frontmatter":
                        self.frontmatter_edit_requested.emit("weekly")
                    elif script.name == "Restart Application":
                        self.restart_requested.emit()
                    elif script.name == "Exit Application":
                        self.exit_requested.emit()
                else:
                    # Regular script execution
                    self.script_selected.emit(script.name, script.path)

    def keyPressEvent(self, event) -> None:
        """
        Handle keyboard events for navigation and execution.

        Args:
            event: The key press event
        """
        if event.key() == Qt.Key.Key_Escape:
            self.hide_animated()
            event.accept()
        elif event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            self._execute_selected()
            event.accept()
        elif event.key() in (Qt.Key.Key_Down, Qt.Key.Key_Up):
            # Forward arrow keys to list for navigation
            self.script_list.setFocus()
            self.script_list.keyPressEvent(event)
            # Return focus to search input
            self.search_input.setFocus()
            event.accept()
        else:
            super().keyPressEvent(event)


    def _resize_keeping_position(self) -> None:
        """Resize the dialog while keeping its top position fixed."""
        # Process pending events to ensure list widget has resized
        QApplication.processEvents()

        # Save current geometry
        current_x: int = self.x()
        current_y: int = self.y()
        current_width: int = self.width()

        # Calculate required height
        search_height = 40
        margins = 16  # Top + bottom margins (8 + 8)
        list_height: int = (
            self.script_list.height() if self.script_list.isVisible() else 0
        )

        total_height: int = search_height + list_height + margins

        # Set fixed size to prevent layout from overriding
        self.setFixedSize(current_width, total_height)

        # Position at saved coordinates
        self.move(current_x, current_y)

        # Process events to apply changes immediately
        QApplication.processEvents()

        # Remove fixed size constraint to allow future resizes
        self.setMaximumSize(16777215, 16777215)
        self.setMinimumSize(0, 0)

    def _center_window(self) -> None:
        """Position the window at the top-center of the screen, Flow Launcher style."""
        # Get the screen that contains the cursor
        cursor_pos = (
            QApplication.instance().primaryScreen().availableGeometry().center()
        )
        screen = QApplication.screenAt(cursor_pos)

        if screen is None:
            # Fallback to primary screen if cursor screen not found
            screen = QApplication.primaryScreen()

        # Get the screen's available geometry (excludes taskbar)
        screen_geometry = screen.availableGeometry()

        # Calculate horizontal center
        x: int = screen_geometry.x() + (screen_geometry.width() - self.width()) // 2

        # Position at ~20% from top (Flow Launcher style)
        y: int = screen_geometry.y() + int(screen_geometry.height() * 0.20)

        # Move dialog to position
        self.move(x, y)

    def showEvent(self, event) -> None:
        """
        Handle dialog show event to reset and center the window.

        Args:
            event: The show event
        """
        super().showEvent(event)

        # Reload scripts in case they changed
        self._load_scripts()

        # Clear search input and list, hide list
        self.search_input.clear()
        self.script_list.clear()
        self.script_list.setMaximumHeight(0)
        self.script_list.setMinimumHeight(0)
        self.script_list.hide()

        # Set explicit initial size (search bar only)
        search_height = 40
        margins = 16  # Top + bottom margins (8 + 8)
        initial_height = search_height + margins
        self.setFixedSize(650, initial_height)

        # Process pending events to ensure geometry is updated
        QApplication.processEvents()

        # Center on screen
        self._center_window()

        # Activate and raise the window to ensure it gets focus
        self.activateWindow()
        self.raise_()

        # Set focus after window is positioned and activated
        self.search_input.setFocus()

        # Start fade in animation
        self.setWindowOpacity(0.0)
        self.fade_in.start()
