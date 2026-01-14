"""
Configuration manager for Obsidian Forge application.
Handles settings for vault path, Node.js path, and Tokyo Night theme configuration.
"""

# ----- Built-In Modules-----
import json
import os
from pathlib import Path
from typing import Optional

# ══════════════════════════════════════════════════════════════════
# APPLICATION METADATA
# ══════════════════════════════════════════════════════════════════
APP_NAME = "Obsidian Forge"
APP_VERSION = "1.0.0"
AUTHOR = "Aaqil"

# ══════════════════════════════════════════════════════════════════
# VAULT PATHS
# ══════════════════════════════════════════════════════════════════
DAILY_SCRIPTS_PATH = "98 - Organize/Scripts/Add to Daily Note"
WEEKLY_SCRIPTS_PATH = "98 - Organize/Scripts/Add to Weekly Note"
UTILS_SCRIPTS_PATH = "98 - Organize/Scripts/Utils"

# ══════════════════════════════════════════════════════════════════
# FONT SETTINGS
# ══════════════════════════════════════════════════════════════════
FONT_FAMILY = "JetBrainsMono Nerd Font"
FONT_SIZE_TITLE = 20
FONT_SIZE_HEADER = 13
FONT_SIZE_LABEL = 11
FONT_SIZE_TEXT = 10
FONT_SIZE_SMALL = 9

# ══════════════════════════════════════════════════════════════════
# UI DIMENSIONS
# ══════════════════════════════════════════════════════════════════
WINDOW_MIN_WIDTH = 750
WINDOW_MIN_HEIGHT = 550
BORDER_RADIUS = 8
BORDER_RADIUS_SMALL = 6
BORDER_RADIUS_LARGE = 12
PADDING = 16
PADDING_SMALL = 12
PADDING_LARGE = 24
SPACING = 12
SPACING_SMALL = 8
SPACING_LARGE = 16

# ══════════════════════════════════════════════════════════════════
# ANIMATION SETTINGS
# ══════════════════════════════════════════════════════════════════
ANIMATION_DURATION = 200  # milliseconds
HOVER_DURATION = 150  # milliseconds


class Config:
    """Configuration manager for application settings."""

    def __init__(self) -> None:
        # Get username and sanitize it for use in filename
        username: str = (
            os.getlogin().replace(" ", "_").replace("\\", "_").replace("/", "_")
        )

        # Use %APPDATA%/Obsidian Forge/ directory
        appdata = os.getenv("APPDATA")
        if appdata:
            self.config_dir: Path = Path(appdata) / APP_NAME
        else:
            # Fallback to user home if APPDATA is not set
            self.config_dir = Path.home() / ".obsidian-forge"

        # Config file named by username
        self.config_file: Path = self.config_dir / f"{username.lower()}.config.json"
        self.settings = self._load_settings()

    def _load_settings(self) -> dict:
        """Load settings from config file or return defaults."""
        if self.config_file.exists():
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading config: {e}")
                return self._default_settings()
        return self._default_settings()

    def _default_settings(self) -> dict:
        """Return default settings."""
        return {
            "vault_path": "",
            "nodejs_path": "node",  # Default to 'node' in PATH
            "theme": "tokyo-night",
            "enable_animations": True,
        }

    def save_settings(self) -> bool:
        """Save current settings to config file."""
        try:
            self.config_dir.mkdir(parents=True, exist_ok=True)
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(self.settings, f, indent=4)
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False

    @property
    def vault_path(self) -> str:
        """Get vault path."""
        return self.settings.get("vault_path", "")

    @vault_path.setter
    def vault_path(self, path: str) -> None:
        """Set vault path."""
        self.settings["vault_path"] = path

    @property
    def nodejs_path(self) -> str:
        """Get Node.js path."""
        return self.settings.get("nodejs_path", "node")

    @nodejs_path.setter
    def nodejs_path(self, path: str) -> None:
        """Set Node.js path."""
        self.settings["nodejs_path"] = path

    @property
    def enable_animations(self) -> bool:
        """Get animation enable setting."""
        return self.settings.get("enable_animations", True)

    @enable_animations.setter
    def enable_animations(self, enabled: bool) -> None:
        """Set animation enable setting."""
        self.settings["enable_animations"] = enabled

    def get_daily_scripts_path(self) -> Optional[Path]:
        """Get full path to daily scripts directory."""
        if not self.vault_path:
            return None
        return Path(self.vault_path) / DAILY_SCRIPTS_PATH

    def get_weekly_scripts_path(self) -> Optional[Path]:
        """Get full path to weekly scripts directory."""
        if not self.vault_path:
            return None
        return Path(self.vault_path) / WEEKLY_SCRIPTS_PATH

    def get_utils_scripts_path(self) -> Optional[Path]:
        """Get full path to utils scripts directory."""
        if not self.vault_path:
            return None
        return Path(self.vault_path) / UTILS_SCRIPTS_PATH

    def is_configured(self) -> bool:
        """Check if all required settings are configured."""
        return bool(self.vault_path and os.path.exists(self.vault_path))

    def validate_paths(self) -> list[str]:
        """Validate configured paths and return list of errors."""
        errors = []

        if not self.vault_path:
            errors.append("Vault path is not set")
        elif not os.path.exists(self.vault_path):
            errors.append(f"Vault path does not exist: {self.vault_path}")
        else:
            # Check if scripts directories exist
            daily_path = self.get_daily_scripts_path()
            if not daily_path or not daily_path.exists():
                errors.append(
                    f"Daily scripts directory not found: {DAILY_SCRIPTS_PATH}"
                )

            weekly_path = self.get_weekly_scripts_path()
            if not weekly_path or not weekly_path.exists():
                errors.append(
                    f"Weekly scripts directory not found: {WEEKLY_SCRIPTS_PATH}"
                )

            utils_path = self.get_utils_scripts_path()
            if not utils_path or not utils_path.exists():
                errors.append(
                    f"Utils scripts directory not found: {UTILS_SCRIPTS_PATH}"
                )

        # Check Node.js
        import subprocess

        try:
            subprocess.run(
                [self.nodejs_path, "--version"],
                capture_output=True,
                check=True,
                timeout=5,
            )
        except (
            subprocess.CalledProcessError,
            FileNotFoundError,
            subprocess.TimeoutExpired,
        ):
            errors.append(f"Node.js not found or not working: {self.nodejs_path}")

        return errors
