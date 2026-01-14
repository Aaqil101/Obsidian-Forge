"""
Script executor for running JavaScript files with Node.js.
Creates a wrapper to simulate the Obsidian QuickAdd API.
"""

# ----- Built-In Modules-----
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Dict

# ----- Core Modules-----
from src.core.config import Config


class ScriptExecutor:
    """Executes JavaScript scripts using Node.js with a simulated QuickAdd API."""

    def __init__(self, config: Config) -> None:
        self.config: Config = config

    def create_wrapper_script(self, script_path: Path, user_input: str) -> str:
        """
        Create a Node.js wrapper script that simulates the Obsidian environment.

        Args:
            script_path: Path to the JavaScript script to execute
            user_input: User input to pass to the script

        Returns:
            JavaScript code as a string
        """
        vault_path_escaped: str = str(self.config.vault_path).replace("\\", "\\\\")
        script_path_escaped: str = str(script_path).replace("\\", "\\\\")
        user_input_escaped: str = (
            user_input.replace("\\", "\\\\").replace("'", "\\'").replace("\n", "\\n")
        )

        wrapper = f"""
const fs = require('fs');
const path = require('path');

// Simulate Obsidian app.vault API
const app = {{
    vault: {{
        adapter: {{
            read: function(filePath) {{
                const fullPath = path.join('{vault_path_escaped}', filePath);
                return fs.promises.readFile(fullPath, 'utf-8');
            }}
        }},
        getAbstractFileByPath: function(filePath) {{
            const fullPath = path.join('{vault_path_escaped}', filePath);
            if (fs.existsSync(fullPath)) {{
                return {{
                    path: filePath,
                    fullPath: fullPath
                }};
            }}
            return null;
        }},
        read: function(file) {{
            return fs.promises.readFile(file.fullPath, 'utf-8');
        }},
        modify: function(file, content) {{
            return fs.promises.writeFile(file.fullPath, content, 'utf-8');
        }}
    }}
}};

// Simulate Notice API
class Notice {{
    constructor(message, duration) {{
        console.log('NOTICE:', message);
        this.message = message;
    }}
}}

// Make these global
global.app = app;
global.Notice = Notice;

// Simulate QuickAdd API
const quickAddApi = {{
    wideInputPrompt: function(title, placeholder) {{
        // Return the user input provided
        return Promise.resolve('{user_input_escaped}');
    }}
}};

// Load and execute the script
const scriptModule = require('{script_path_escaped}');

// Execute the script
scriptModule({{ quickAddApi }})
    .then(() => {{
        console.log('SCRIPT_COMPLETE');
        process.exit(0);
    }})
    .catch((error) => {{
        console.error('SCRIPT_ERROR:', error.message);
        process.exit(1);
    }});
"""
        return wrapper

    def execute_script(self, script_path: Path, user_input: str) -> Dict[str, Any]:
        """
        Execute a JavaScript script with the given user input.

        Args:
            script_path: Path to the JavaScript script
            user_input: User input to pass to the script

        Returns:
            Dictionary with 'success' (bool), 'output' (str), and 'error' (str or None)
        """
        try:
            # Create wrapper script
            wrapper_code: str = self.create_wrapper_script(script_path, user_input)

            # Write wrapper to temp file
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".js", delete=False, encoding="utf-8"
            ) as f:
                temp_script: str = f.name
                f.write(wrapper_code)

            # Execute with Node.js
            result = subprocess.run(
                [self.config.nodejs_path, temp_script],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=str(
                    self.config.vault_path
                ),  # Run in vault directory for relative paths
            )

            # Clean up temp file
            try:
                Path(temp_script).unlink()
            except:
                pass

            # Parse output
            output_lines: list[str] = result.stdout.strip().split("\n")
            notices: list[str] = [
                line.replace("NOTICE:", "").strip()
                for line in output_lines
                if line.startswith("NOTICE:")
            ]

            if result.returncode == 0:
                return {
                    "success": True,
                    "output": (
                        "\n".join(notices)
                        if notices
                        else "Script executed successfully"
                    ),
                    "error": None,
                }
            else:
                error_msg = result.stderr or "Unknown error"
                return {
                    "success": False,
                    "output": "\n".join(notices) if notices else "",
                    "error": error_msg,
                }

        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "output": "",
                "error": "Script execution timed out (30 seconds)",
            }
        except Exception as e:
            return {"success": False, "output": "", "error": str(e)}

    def get_available_scripts(self, script_type: str) -> list[Dict[str, str]]:
        """
        Get list of available scripts for a given type.

        Args:
            script_type: 'daily' or 'weekly'

        Returns:
            List of dictionaries with 'name', 'path', and 'icon' keys
        """
        if script_type == "daily":
            scripts_dir = self.config.get_daily_scripts_path()
        elif script_type == "weekly":
            scripts_dir = self.config.get_weekly_scripts_path()
        else:
            return []

        if not scripts_dir or not scripts_dir.exists():
            return []

        scripts = []
        for script_file in sorted(scripts_dir.glob("*.js")):
            if script_file.stem.endswith(".bak"):
                continue

            # Parse script name and icon from filename
            name: str = (
                script_file.stem.replace("add-daily-", "")
                .replace("add-weekly-", "")
                .replace("-", " ")
                .title()
            )

            # Assign icons based on script name
            icon_map: Dict[str, str] = {
                "win": "🏆",
                "gratitude": "🙏",
                "dream": "💭",
                "sleep": "😴",
                "review": "📝",
                "journal entries": "📓",
                "progress": "📈",
                "open loops": "🔄",
                "discovery": "🔍",
                "miss": "❌",
            }

            icon: str = icon_map.get(name.lower(), "📌")

            scripts.append({"name": name, "path": str(script_file), "icon": icon})

        return scripts
