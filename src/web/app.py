"""
Flask application factory for media library web server.
"""

from flask import Flask
from pathlib import Path
import logging


def create_app(vault_path: str, config_dict: dict):
    """
    Create and configure Flask application.

    Args:
        vault_path: Path to Obsidian vault
        config_dict: Dictionary with media library configuration

    Returns:
        Configured Flask application
    """
    # Get paths for static files and templates
    web_dir = Path(__file__).parent
    static_folder = web_dir / "static"
    template_folder = web_dir / "templates"

    app = Flask(
        __name__, static_folder=str(static_folder), template_folder=str(template_folder)
    )

    # Store configuration
    app.config["VAULT_PATH"] = vault_path
    app.config["MEDIA_CONFIG"] = config_dict

    # Disable Flask's default logger noise in production
    log = logging.getLogger("werkzeug")
    log.setLevel(logging.ERROR)

    # Register blueprints
    from src.web.routes import api_bp, main_bp

    app.register_blueprint(api_bp, url_prefix="/api")
    app.register_blueprint(main_bp)

    return app
