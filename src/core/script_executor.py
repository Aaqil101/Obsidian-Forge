"""
Script executor for running JavaScript files with Node.js.
Creates a wrapper to simulate the Obsidian QuickAdd API.
"""

# ----- Built-In Modules-----
import json
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

# ----- Core Modules-----
from src.core.config import Config


@dataclass
class SleepScriptInputs:
    """Pre-collected inputs for the sleep script."""

    sleep_wake_times: str  # The sleep/wake time string with date prefix
    quality: Optional[str]  # Excellent, Good, Fair, Poor, Restless, or None (Skip)
    had_dreams: bool  # Whether user had dreams
    dream_descriptions: str  # Multi-line dream descriptions (empty if no dreams)


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

        wrapper: str = f"""
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
                error_msg: str = result.stderr or "Unknown error"
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

    def create_sleep_wrapper_script(
        self, script_path: Path, inputs: SleepScriptInputs
    ) -> str:
        """
        Create a Node.js wrapper script specifically for the sleep script.

        This wrapper pre-populates all the QuickAdd API responses with the
        collected input data, so the script can run non-interactively.

        Args:
            script_path: Path to the add-daily-sleep.js script
            inputs: Pre-collected sleep input data

        Returns:
            JavaScript code as a string
        """
        vault_path_escaped: str = str(self.config.vault_path).replace("\\", "\\\\")
        script_path_escaped: str = str(script_path).replace("\\", "\\\\")

        # Escape the sleep/wake times string
        sleep_wake_escaped: str = (
            inputs.sleep_wake_times.replace("\\", "\\\\")
            .replace("'", "\\'")
            .replace("\n", "\\n")
        )

        # Quality value (null if skipped)
        quality_js: str = f"'{inputs.quality}'" if inputs.quality else "null"

        # Dreams value
        had_dreams_js = "true" if inputs.had_dreams else "false"

        # Dream descriptions (escaped)
        dream_desc_escaped: str = (
            inputs.dream_descriptions.replace("\\", "\\\\")
            .replace("'", "\\'")
            .replace("\n", "\\n")
        )

        wrapper = f"""
const fs = require('fs');
const path = require('path');

// Pre-collected inputs from Python UI
const PRECOLLECTED_INPUTS = {{
    sleepWakeTimes: '{sleep_wake_escaped}',
    quality: {quality_js},
    hadDreams: {had_dreams_js},
    dreamDescriptions: '{dream_desc_escaped}'
}};

// Track which prompts have been called to return appropriate values
let suggesterCallCount = 0;
let wideInputCallCount = 0;

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

// Simulate QuickAdd API with pre-collected responses
const quickAddApi = {{
    wideInputPrompt: function(title, placeholder) {{
        wideInputCallCount++;
        // First call: sleep/wake times, Second call: dream descriptions
        if (wideInputCallCount === 1) {{
            return Promise.resolve(PRECOLLECTED_INPUTS.sleepWakeTimes);
        }} else {{
            return Promise.resolve(PRECOLLECTED_INPUTS.dreamDescriptions);
        }}
    }},

    suggester: function(displayItems, actualValues) {{
        suggesterCallCount++;
        // First suggester call: time entry selection (we use custom since we have the time)
        // Second suggester call: sleep quality
        if (suggesterCallCount === 1) {{
            // Return "CUSTOM" to trigger custom time entry path
            // since we already have the time in sleepWakeTimes
            return Promise.resolve('CUSTOM');
        }} else {{
            // Sleep quality selection
            return Promise.resolve(PRECOLLECTED_INPUTS.quality);
        }}
    }},

    yesNoPrompt: function(question) {{
        // Did you have any dreams?
        return Promise.resolve(PRECOLLECTED_INPUTS.hadDreams);
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
        console.error(error.stack);
        process.exit(1);
    }});
"""
        return wrapper

    def execute_sleep_script(
        self, script_path: Path, inputs: SleepScriptInputs
    ) -> Dict[str, Any]:
        """
        Execute the sleep script with pre-collected inputs.

        Args:
            script_path: Path to the add-daily-sleep.js script
            inputs: Pre-collected sleep input data

        Returns:
            Dictionary with 'success' (bool), 'output' (str), and 'error' (str or None)
        """
        try:
            # Create wrapper script
            wrapper_code: str = self.create_sleep_wrapper_script(script_path, inputs)

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
                cwd=str(self.config.vault_path),
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
                        else "Sleep entry added successfully"
                    ),
                    "error": None,
                }
            else:
                error_msg: str = result.stderr or "Unknown error"
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

            # Assign icons based on script name (SVG file names)
            icon_map: Dict[str, str] = {
                "win": "daily-weekly/win.svg",
                "gratitude": "daily-weekly/gratitude.svg",
                "dream": "daily-weekly/dream.svg",
                "sleep": "daily-weekly/sleep.svg",
                "review": "daily-weekly/review.svg",
                "journal entries": "daily-weekly/journal_entries.svg",
                "progress": "daily-weekly/progress.svg",
                "open loops": "daily-weekly/open_loops.svg",
                "discovery": "daily-weekly/discovery.svg",
                "miss": "daily-weekly/miss.svg",
            }

            icon: str = icon_map.get(name.lower(), "file.svg")

            scripts.append({"name": name, "path": str(script_file), "icon": icon})

        return scripts
