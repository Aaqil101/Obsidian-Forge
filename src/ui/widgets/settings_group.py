"""
Collapsible settings group widget for Obsidian Forge.
Adapted from Blender-Launcher-V2 design patterns.
"""

# ----- Built-In Modules-----
from typing import List

# ----- PySide6 Modules -----
from PySide6.QtCore import QSize, Signal, Slot
from PySide6.QtGui import QFont, QFontDatabase
from PySide6.QtWidgets import (
    QCheckBox,
    QFrame,
    QGridLayout,
    QLabel,
    QLayout,
    QPushButton,
    QWidget,
)

# ----- Core Modules -----
from src.core import FONT_SIZE_HEADER

# ----- Utils Modules -----
from src.utils import get_icon


class SettingsGroup(QFrame):
    """
    Collapsible group widget for organizing settings.

    Signals:
        collapsed(bool): Emitted when the group is collapsed/expanded
        checked(bool): Emitted when the checkbox is toggled (if checkable)
    """

    collapsed = Signal(bool)
    checked = Signal(bool)

    def __init__(
        self, label: str, *, checkable: bool = False, parent: QWidget | None = None
    ) -> None:
        """
        Create a collapsible settings group.

        Args:
            label: The group title text
            checkable: If True, shows a checkbox instead of plain label
            parent: Parent widget (optional)
        """
        super().__init__(parent)
        self.setContentsMargins(0, 0, 0, 0)
        self.setProperty("SettingsGroup", True)

        self._layout = QGridLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)

        # Collapse/expand button - compact size
        self.collapse_button = QPushButton(self)
        self.collapse_button.setProperty("CollapseButton", True)
        self.collapse_button.setFixedSize(18, 18)
        self.collapse_button.setIcon(get_icon("expand_less.svg", color="#7aa2f7"))
        self.collapse_button.setIconSize(QSize(10, 10))
        self.collapse_button.clicked.connect(self.toggle)
        self._layout.addWidget(self.collapse_button, 0, 0, 1, 1)

        # Label or checkbox
        self._checkable: bool = checkable
        if checkable:
            self.checkbutton = QCheckBox(self)
            self.checkbutton.setText(label)
            self.checkbutton.clicked.connect(self.checked.emit)
            self._layout.addWidget(self.checkbutton, 0, 1, 1, 1)
            self.label = None
        else:
            self.checkbutton = None
            self.label = QLabel(f" {label}")
            self.label.setProperty("SectionHeader", True)

            # Load and apply OpenSans-SemiBold font
            font_id: int = QFontDatabase.addApplicationFont(
                "assets/fonts/OpenSans-SemiBold.ttf"
            )
            if font_id != -1:
                font_families: List[str] = QFontDatabase.applicationFontFamilies(
                    font_id
                )
                if font_families:
                    font = QFont(font_families[0])
                    font.setPointSize(FONT_SIZE_HEADER)
                    self.label.setFont(font)

            self._layout.addWidget(self.label, 0, 1, 1, 1)

        self._widget = None
        self._collapsed = False

    @Slot(QWidget)
    def setWidget(self, w: QWidget) -> None:
        """Set the content widget of this group."""
        if self._widget == w:
            return

        if self._widget is not None:
            self._layout.removeWidget(self._widget)

        self._widget = w
        self._layout.addWidget(self._widget, 1, 0, 1, 2)

    @Slot(QLayout)
    def setLayout(self, layout: QLayout) -> None:
        """Set the content layout of this group."""
        if self._widget is not None:
            self._layout.removeWidget(self._widget)

        self._widget = QWidget()
        self._widget.setLayout(layout)
        self._layout.addWidget(self._widget, 1, 0, 1, 2)

    @Slot(bool)
    def set_collapsed(self, collapsed: bool) -> None:
        """Set the collapsed state."""
        if collapsed and not self._collapsed:
            self.collapse()
        elif not collapsed and self._collapsed:
            self.uncollapse()

    @Slot()
    def toggle(self) -> None:
        """Toggle between collapsed and expanded states."""
        self.set_collapsed(not self._collapsed)

    @Slot()
    def collapse(self) -> None:
        """Collapse the group to hide its content."""
        if self._widget is None:
            return

        self._widget.hide()
        self.collapse_button.setIcon(get_icon("expand_more.svg", color="#7aa2f7"))
        self._collapsed = True
        self.collapsed.emit(True)

        if self.parent():
            self.parent().updateGeometry()

    @Slot()
    def uncollapse(self) -> None:
        """Expand the group to show its content."""
        if self._widget is None:
            return

        self._widget.show()
        self.collapse_button.setIcon(get_icon("expand_less.svg", color="#7aa2f7"))
        self._collapsed = False
        self.collapsed.emit(False)

        if self.parent():
            self.parent().updateGeometry()

    def isCollapsed(self) -> bool:
        """Return whether the group is currently collapsed."""
        return self._collapsed

    def setChecked(self, checked: bool) -> None:
        """Set the checkbox state (if checkable)."""
        if self._checkable and self.checkbutton:
            self.checkbutton.setChecked(checked)

    def isChecked(self) -> bool:
        """Return the checkbox state (if checkable)."""
        if self._checkable and self.checkbutton:
            return self.checkbutton.isChecked()
        return False
