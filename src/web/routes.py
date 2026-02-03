"""
Flask routes for media library API.
"""

from flask import Blueprint, jsonify, request, send_from_directory, render_template, current_app
from pathlib import Path
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.config import Config
from web.media_parser import get_all_media_items, parse_media_file
from urllib.parse import quote

# Blueprints
api_bp = Blueprint("api", __name__)
main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    """Serve the main HTML page."""
    return render_template("index.html")


@api_bp.route("/media", methods=["GET"])
def get_media():
    """
    Get all media items, optionally filtered by type.

    Query parameters:
        type: Optional filter (books, movies, tv_shows, youtube, documentaries)

    Returns:
        JSON object with media items organized by type
    """
    try:
        # Create config from stored vault path
        config = Config()
        config.vault_path = current_app.config["VAULT_PATH"]

        # Get all media items
        media_data = get_all_media_items(config)

        # Filter by type if specified
        media_type = request.args.get("type")
        if media_type and media_type in media_data:
            media_data = {media_type: media_data[media_type]}

        # Convert MediaItem objects to dictionaries
        result = {}
        vault_path = Path(current_app.config["VAULT_PATH"])

        for type_key, items in media_data.items():
            result[type_key] = []
            for item in items:
                # Get cover image based on media type with local-first fallback
                cover_image = None

                if type_key == "youtube":
                    # Try local thumbnail first
                    thumbnail = getattr(item, "thumbnail", None)
                    if thumbnail:
                        # Extract filename from wiki link format [[filename.jpg]]
                        if thumbnail.startswith("[[") and thumbnail.endswith("]]"):
                            thumbnail_filename = thumbnail[2:-2]
                        else:
                            thumbnail_filename = thumbnail

                        # Check if file exists in vault
                        thumbnail_path = vault_path / thumbnail_filename
                        if thumbnail_path.exists():
                            cover_image = f"/vault/{thumbnail_filename}"
                        else:
                            # Fall back to URL
                            cover_image = getattr(item, "thumbnail_url", None)
                    else:
                        # No local thumbnail, use URL
                        cover_image = getattr(item, "thumbnail_url", None)

                elif type_key == "books":
                    # Try local cover first
                    local_cover = getattr(item, "localCover", None)
                    if local_cover:
                        # Check if file exists in vault
                        local_cover_path = vault_path / local_cover
                        if local_cover_path.exists():
                            cover_image = f"/vault/{local_cover}"
                        else:
                            # Fall back to URL cover
                            cover_image = getattr(item, "cover", None)
                    else:
                        # No local cover, use URL cover
                        cover_image = getattr(item, "cover", None)

                elif type_key in ["movies", "tv_shows", "documentaries"]:
                    poster = getattr(item, "poster", None)
                    # Prepend /vault/ to local file paths so Flask can serve them
                    if poster and not poster.startswith(("http://", "https://", "/vault/")):
                        cover_image = f"/vault/{poster}"
                    else:
                        cover_image = poster

                result[type_key].append({
                    "id": item.id,
                    "title": item.title,
                    "media_type": item.media_type,
                    "cover_image": cover_image,
                    "rating": item.rating,
                    "status": getattr(item, "status", ""),
                    "year": item.year,
                    "metadata": item.metadata,
                })

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api_bp.route("/media/<media_type>/<item_id>", methods=["GET"])
def get_media_detail(media_type, item_id):
    """
    Get detailed view of a single media item.

    Args:
        media_type: Type of media
        item_id: ID of the item (filename without extension)

    Returns:
        JSON object with full media item details
    """
    try:
        config = Config()
        config.vault_path = current_app.config["VAULT_PATH"]

        # Get the appropriate directory path
        if media_type == "books":
            directory = config.get_books_path()
        elif media_type == "youtube":
            directory = config.get_youtube_path()
        elif media_type == "movies":
            directory = config.get_movies_path()
        elif media_type == "tv_shows":
            directory = config.get_tv_shows_path()
        elif media_type == "documentaries":
            directory = config.get_documentaries_path()
        else:
            return jsonify({"error": "Invalid media type"}), 400

        if not directory or not directory.exists():
            return jsonify({"error": "Media directory not found"}), 404

        # Find the file
        file_path = None
        for md_file in directory.rglob(f"{item_id}.md"):
            file_path = md_file
            break

        if not file_path:
            return jsonify({"error": "Item not found"}), 404

        # Parse the file
        item = parse_media_file(file_path, media_type)
        if not item:
            return jsonify({"error": "Failed to parse item"}), 500

        return jsonify(
            {
                "id": item.id,
                "title": item.title,
                "media_type": item.media_type,
                "cover_image": item.cover_image,
                "rating": item.rating,
                "status": item.status,
                "year": item.year,
                "metadata": item.metadata,
                "file_path": item.file_path,
            }
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api_bp.route("/open/<media_type>/<item_id>", methods=["POST"])
def open_in_obsidian(media_type, item_id):
    """
    Generate Obsidian URI to open the file.

    Args:
        media_type: Type of media
        item_id: ID of the item

    Returns:
        JSON object with Obsidian URI
    """
    try:
        config = Config()
        vault_path = current_app.config["VAULT_PATH"]
        config.vault_path = vault_path

        # Get the appropriate directory path
        if media_type == "books":
            directory = config.get_books_path()
        elif media_type == "youtube":
            directory = config.get_youtube_path()
        elif media_type == "movies":
            directory = config.get_movies_path()
        elif media_type == "tv_shows":
            directory = config.get_tv_shows_path()
        elif media_type == "documentaries":
            directory = config.get_documentaries_path()
        else:
            return jsonify({"error": "Invalid media type"}), 400

        if not directory or not directory.exists():
            return jsonify({"error": "Media directory not found"}), 404

        # Find the file
        file_path = None
        for md_file in directory.rglob(f"{item_id}.md"):
            file_path = md_file
            break

        if not file_path:
            return jsonify({"error": "Item not found"}), 404

        # Get vault name (last part of vault path)
        vault_name = Path(vault_path).name

        # Get relative file path from vault root
        relative_path = file_path.relative_to(vault_path)

        # Create Obsidian URI
        obsidian_uri = f"obsidian://open?vault={quote(vault_name)}&file={quote(str(relative_path).replace('\\', '/'))}"

        return jsonify({"uri": obsidian_uri})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@main_bp.route("/vault/<path:filepath>")
def serve_vault_file(filepath):
    """
    Serve files from the vault (for cover images).

    Args:
        filepath: Relative path from vault root

    Returns:
        File from vault
    """
    try:
        vault_path = current_app.config["VAULT_PATH"]
        return send_from_directory(vault_path, filepath)
    except Exception as e:
        return jsonify({"error": str(e)}), 404
