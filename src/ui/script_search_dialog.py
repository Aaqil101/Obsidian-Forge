"""
Script search dialog for quick access to scripts without opening main window.
Flow Launcher-style searchable list of all available scripts (daily + weekly).
"""

# ----- Built-In Modules -----
from dataclasses import dataclass

# ----- PySide6 Modules -----
from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
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
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(12)

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
        title_label.setStyleSheet("color: #c0caf5; font-weight: 500;")
        text_layout.addWidget(title_label)

        # Subtitle (script type and path)
        if script.is_system_action:
            subtitle_text = "System action"
        else:
            subtitle_text = (
                f"{'Daily' if script.script_type == 'daily' else 'Weekly'} script"
            )
        subtitle_label = QLabel(subtitle_text)
        subtitle_label.setFont(QFont(FONT_FAMILY, 9))
        subtitle_label.setStyleSheet("color: #565f89;")
        text_layout.addWidget(subtitle_label)

        layout.addLayout(text_layout)

        # Spacer to push badge to the right
        layout.addStretch()

        # Badge for script type (only for scripts, not system actions)
        if not script.is_system_action:
            badge_label = QLabel("[D]" if script.script_type == "daily" else "[W]")
            badge_label.setFont(QFont(FONT_FAMILY, 9))
            badge_label.setStyleSheet(
                """
                color: #565f89;
                background-color: rgba(86, 95, 137, 0.2);
                border-radius: 4px;
                padding: 2px 6px;
                """
            )
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
    restart_requested = Signal()  # Request application restart

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
        self.setWindowFlags(
            Qt.WindowType.Tool
            | Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
        )
        self.setWindowTitle("Obsidian Forge")
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedWidth(650)

        self._setup_ui()
        self._apply_styles()
        self._load_scripts()

    def _setup_ui(self) -> None:
        """Setup the dialog UI - Flow Launcher style."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(8)

        # Search input with icon on right (Spotlight style)
        self.search_input = QLineEdit()
        self.search_input.setProperty("SearchBar", True)
        self.search_input.setPlaceholderText("Search scripts...")
        self.search_input.setFont(QFont(FONT_FAMILY, 13))
        self.search_input.setMinimumHeight(50)
        self.search_input.textChanged.connect(self._filter_scripts)
        # Search icon on the right side (trailing position)
        self.search_input.addAction(
            get_icon("search.svg"),
            QLineEdit.ActionPosition.TrailingPosition,
        )
        main_layout.addWidget(self.search_input)

        # Script list with larger items (initially hidden)
        self.script_list = QListWidget()
        self.script_list.setFont(QFont(FONT_FAMILY, 11))
        self.script_list.setIconSize(QSize(32, 32))
        self.script_list.setSpacing(4)
        self.script_list.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.script_list.itemClicked.connect(self._on_item_clicked)
        self.script_list.itemActivated.connect(self._on_item_activated)
        self.script_list.hide()  # Start hidden
        main_layout.addWidget(self.script_list)

    def _apply_styles(self) -> None:
        """Apply Spotlight/Raycast-style CSS to the dialog."""
        # Main dialog styling - transparent background
        self.setStyleSheet(
            """
            QDialog {
                background-color: transparent;
            }
            """
        )

        # List widget styling with background
        self.script_list.setStyleSheet(
            """
            QListWidget {
                background-color: rgba(26, 27, 38, 0.95);
                border: 1px solid #414868;
                border-radius: 10px;
                outline: none;
                padding: 6px;
            }
            QListWidget::item {
                border-radius: 6px;
                padding: 0px;
                margin: 2px 0px;
                background-color: transparent;
            }
            QListWidget::item:hover {
                background-color: rgba(125, 207, 255, 0.1);
            }
            QListWidget::item:selected {
                background-color: rgba(125, 207, 255, 0.15);
            }
            QListWidget::item:selected:hover {
                background-color: rgba(125, 207, 255, 0.2);
            }
            """
        )

    def _load_scripts(self) -> None:
        """Load all scripts (daily + weekly) from the executor into memory only."""
        self.all_scripts.clear()

        # Add system actions first
        restart_item = ScriptSearchItem(
            name="Restart Application",
            path="",
            icon="refresh.svg",
            script_type="system",
            display_text="Restart Application",
            is_system_action=True,
        )
        self.all_scripts.append(restart_item)

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
        item.setSizeHint(QSize(0, 56))

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
            self.script_list.hide()
            self.adjustSize()
            return

        # Check for filter prefix
        filter_type = None
        if search_text.startswith("/d"):
            filter_type = "daily"
            search_text = search_text[2:].strip()
        elif search_text.startswith("/w"):
            filter_type = "weekly"
            search_text = search_text[2:].strip()

        # Build filtered list
        visible_count = 0
        for script_data in self.all_scripts:
            # Type filter
            if filter_type and script_data.script_type != filter_type:
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
            placeholder_label.setStyleSheet(
                "color: #565f89; padding: 16px; text-align: center;"
            )
            placeholder_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            placeholder_item.setSizeHint(QSize(0, 48))
            placeholder_item.setFlags(Qt.ItemFlag.NoItemFlags)
            self.script_list.addItem(placeholder_item)
            self.script_list.setItemWidget(placeholder_item, placeholder_label)
            visible_count = 1  # For height calculation

        # Show the list and resize window
        self.script_list.show()
        self.script_list.setFixedHeight(min(400, visible_count * 60 + 20))
        self.adjustSize()

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
                self.hide()
                # Check if it's a system action
                if script.is_system_action:
                    if script.name == "Restart Application":
                        self.restart_requested.emit()
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
            self.hide()
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

    def _center_window(self) -> None:
        """Position the window at the top-center of the screen, Flow Launcher style."""
        # Get the screen that contains the cursor
        cursor_pos = QApplication.instance().primaryScreen().availableGeometry().center()
        screen = QApplication.screenAt(cursor_pos)

        if screen is None:
            # Fallback to primary screen if cursor screen not found
            screen = QApplication.primaryScreen()

        # Get the screen's available geometry (excludes taskbar)
        screen_geometry = screen.availableGeometry()

        # Calculate horizontal center
        x = screen_geometry.x() + (screen_geometry.width() - self.width()) // 2

        # Position at ~20% from top (Flow Launcher style)
        y = screen_geometry.y() + int(screen_geometry.height() * 0.20)

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
        self.script_list.hide()
        self.adjustSize()

        # Process pending events to ensure geometry is updated
        QApplication.processEvents()

        self.search_input.setFocus()

        # Center on screen
        self._center_window()
