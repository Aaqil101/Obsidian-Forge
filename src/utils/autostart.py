"""
Windows autostart utility for Obsidian Forge.
Manages registry entries for running on Windows startup.
"""
import sys
import winreg
from pathlib import Path

REGISTRY_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
APP_NAME = "ObsidianForge"


def get_executable_path() -> str:
    """Get path to executable (handles both dev and packaged scenarios)."""
    if getattr(sys, "frozen", False):
        # Running as compiled executable
        return f'"{sys.executable}"'
    else:
        # Running from source - use pythonw.exe with main.py
        python_dir = Path(sys.executable).parent
        pythonw = python_dir / "pythonw.exe"
        main_py = Path(__file__).parent.parent.parent / "main.py"
        return f'"{pythonw}" "{main_py}"'


def is_autostart_enabled() -> bool:
    """Check if autostart is currently enabled in registry."""
    try:
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER, REGISTRY_KEY, 0, winreg.KEY_READ
        ) as key:
            winreg.QueryValueEx(key, APP_NAME)
            return True
    except FileNotFoundError:
        return False
    except Exception as e:
        print(f"Error checking autostart status: {e}")
        return False


def enable_autostart() -> bool:
    """Enable autostart by adding registry entry."""
    try:
        exe_path = get_executable_path()
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER, REGISTRY_KEY, 0, winreg.KEY_WRITE
        ) as key:
            winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, exe_path)
        return True
    except Exception as e:
        print(f"Error enabling autostart: {e}")
        return False


def disable_autostart() -> bool:
    """Disable autostart by removing registry entry."""
    try:
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER, REGISTRY_KEY, 0, winreg.KEY_WRITE
        ) as key:
            winreg.DeleteValue(key, APP_NAME)
        return True
    except FileNotFoundError:
        return True  # Already not present
    except Exception as e:
        print(f"Error disabling autostart: {e}")
        return False
