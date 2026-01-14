# Obsidian Forge

A PySide6 application for adding bullet points to Obsidian daily and weekly notes, styled with the **Tokyo Night** theme following [GitUI](https://github.com/extrawurst/gitui)'s design patterns.

## Features

- **Tokyo Night Theme**: Beautiful dark theme with carefully chosen colors
- **Nerd Font Icons**: Uses JetBrainsMono Nerd Font for consistent iconography
- **Script Execution**: Run your existing QuickAdd JavaScript scripts
- **Daily & Weekly Notes**: Separate tabs for organizing daily and weekly entries
- **Modern Architecture**: Clean separation of concerns following GitUI's patterns
- **Smart Typography**: Automatically applies smart quotes, em dashes, and ellipsis
- **Date/Week Parsing**: Supports date formats (@YYYY-MM-DD, @MM-DD, @DD) and week formats (@YYYY-Www, @ww)

## Prerequisites

- **Python 3.10+**
- **Node.js**: Required for executing JavaScript scripts
- **JetBrainsMono Nerd Font**: Required for icon display
  - Download from: https://www.nerdfonts.com/font-downloads
  - Install the font on your system
- **Obsidian vault** with QuickAdd scripts at:
  - `98 - Organize/Scripts/Add to Daily Note/`
  - `98 - Organize/Scripts/Add to Weekly Note/`
  - `98 - Organize/Scripts/Utils/`

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/Obsidian-Forge.git
cd Obsidian-Forge
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
# or
source .venv/bin/activate  # Linux/Mac
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the application:
```bash
python main.py
```

### First-Time Setup

On first run, you'll be prompted to configure:

1. **Vault Path**: Path to your Obsidian vault
2. **Node.js Path**: Path to Node.js executable (or just "node" if in PATH)

Settings are stored in `%APPDATA%\Obsidian Forge\{username}_config.json` (Windows) or `~/.obsidian-forge/{username}_config.json` (Linux/Mac).

### Keyboard Shortcuts

- `Ctrl+,` - Open Settings
- `Ctrl+Q` - Quit Application
- `Ctrl+Tab` - Next Tab
- `Ctrl+Shift+Tab` - Previous Tab
- `Alt+1` - Daily Notes Tab
- `Alt+2` - Weekly Notes Tab
- `Ctrl+Return` - Submit (in dialogs)
- `Esc` - Cancel (in dialogs)

## How It Works

The application creates a Node.js wrapper that simulates the Obsidian QuickAdd API and executes your existing JavaScript scripts. This means:

- ✅ Your scripts run exactly as they would in Obsidian
- ✅ All your custom logic and formatting is preserved
- ✅ No need to rewrite scripts in Python
- ✅ Changes to your scripts are immediately reflected in the app

## Project Structure

```
Obsidian-Forge/
├── main.py                 # Application entry point
├── assets/                 # Icons and images
│   ├── obsidian-forge.ico
│   ├── message.ico
│   └── message.png
├── src/
│   ├── __init__.py
│   ├── core/              # Core application logic
│   │   ├── __init__.py
│   │   ├── config.py      # Configuration with Tokyo Night theme
│   │   └── script_executor.py  # JavaScript script execution
│   ├── ui/                # User interface components
│   │   ├── __init__.py
│   │   ├── components.py  # Reusable UI components
│   │   ├── styles.py      # Tokyo Night stylesheets
│   │   ├── main_window.py # Main application window
│   │   └── settings_dialog.py  # Settings dialog
│   └── utils/             # Utility modules
│       ├── __init__.py
│       ├── color.py       # Tokyo Night color constants
│       ├── icons.py       # Nerd Font icon constants
│       └── resources.py   # Resource management with PyInstaller support
└── README.md
```

### Architecture Overview

The project follows **GitUI's architectural patterns** for maintainability and extensibility:

#### 1. **Separation of Concerns**
- **`core/`**: Business logic and configuration
- **`ui/`**: User interface and presentation
- **`utils/`**: Shared utilities and helpers

#### 2. **Three-Layer Styling System**
1. **`utils/color.py`**: Tokyo Night color constants
2. **`ui/styles.py`**: Reusable stylesheet strings and functions
3. **`ui/components.py`**: Component factory functions

#### 3. **Configuration Management**
- Centralized configuration in `core/config.py`
- All theme colors, fonts, and dimensions in one place
- Settings stored in `%APPDATA%/Obsidian Forge/`

#### 4. **Design Patterns**
- **Factory Pattern**: Component creation functions
- **Singleton Pattern**: Configuration manager
- **Resource Management**: PyInstaller-compatible resource loading

## Supported Scripts

The application automatically detects and creates buttons for all `.js` files in your QuickAdd script directories.

### Daily Notes Scripts
- 🏆 Wins
- 🙏 Gratitude
- 💭 Dreams
- 😴 Sleep
- 📝 Review
- 📔 Journal Entries

### Weekly Notes Scripts
- 🏆 Wins
- 📈 Progress
- 🔄 Open Loops
- 💡 Discovery
- 😔 Miss
- 📝 Review

## Troubleshooting

### "Node.js not found or not working"
Make sure Node.js is installed and the path in Settings is correct. Try running `node --version` in your terminal.

### "Daily/Weekly scripts directory not found"
Verify that your vault path is correct and contains the required directory structure:
- `98 - Organize/Scripts/Add to Daily Note/`
- `98 - Organize/Scripts/Add to Weekly Note/`
- `98 - Organize/Scripts/Utils/`

### "Script execution failed"
Check that:
- Your Obsidian vault structure matches what the scripts expect
- The daily/weekly note files exist in the expected locations
- The scripts have the correct section headings (e.g., `### 🏆 Wins`)

## Tokyo Night Theme

The application uses the **Tokyo Night** color palette:

### Colors

| Color | Hex | Usage |
|-------|-----|-------|
| Background Primary | `#1a1b26` | Main background |
| Background Secondary | `#24283b` | Panels, cards |
| Text Primary | `#c0caf5` | Main text |
| Blue | `#7aa2f7` | Primary accent |
| Cyan | `#7dcfff` | Secondary accent |
| Green | `#9ece6a` | Success |
| Red | `#f7768e` | Error |
| Yellow | `#e0af68` | Warning |
| Purple | `#bb9af7` | Info |

### Typography

- **Font**: JetBrainsMono Nerd Font
- **Sizes**: 20pt (title), 13pt (header), 11pt (label), 10pt (text), 9pt (small)

## Configuration

Settings are stored in:
- **Windows**: `%APPDATA%\Obsidian Forge\{username}_config.json`
- **Linux/Mac**: `~/.obsidian-forge/{username}_config.json`

### Configuration Options

```json
{
    "vault_path": "C:/Users/YourName/Documents/Obsidian/YourVault",
    "nodejs_path": "node",
    "theme": "tokyo-night",
    "enable_animations": true
}
```

## Development

### Adding New Features

1. **New UI Components**: Add to `src/ui/components.py`
2. **New Styles**: Add to `src/ui/styles.py`
3. **New Icons**: Add to `src/utils/icons.py`
4. **New Config Options**: Add to `src/core/config.py`

### Code Style

- **Type Hints**: Use throughout
- **Docstrings**: Document all classes and public methods
- **Naming**: `snake_case` for functions/variables, `PascalCase` for classes
- **Constants**: `UPPER_SNAKE_CASE` in `config.py`

## Building for Distribution

To create a standalone executable with PyInstaller:

```bash
pip install pyinstaller
pyinstaller --name="Obsidian Forge" \
            --windowed \
            --icon=assets/obsidian-forge.ico \
            --add-data="assets:assets" \
            main.py
```

The `utils/resources.py` module handles both development and bundled paths automatically.

## Inspired By

This project's architecture and styling are inspired by [GitUI](https://github.com/extrawurst/gitui), a blazing fast terminal UI for Git written in Rust. We've adapted its:

- **Tokyo Night theme** for consistent, beautiful colors
- **Modular architecture** for separation of concerns
- **Component-based design** for reusability
- **Centralized configuration** for maintainability

## License

See [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please follow the existing code style and architectural patterns.

## Acknowledgments

- **Tokyo Night Theme**: Original theme by [enkia](https://github.com/enkia/tokyo-night-vscode-theme)
- **GitUI**: Architectural inspiration and design patterns
- **Nerd Fonts**: Icon fonts for beautiful UI
- **PySide6**: Python bindings for Qt framework
