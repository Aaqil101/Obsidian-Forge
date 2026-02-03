"""
Flask server manager using QThread for background operation.
"""

from PySide6.QtCore import QThread, Signal
import socket
import sys
from pathlib import Path
from werkzeug.serving import make_server

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.config import Config
from web.app import create_app


class FlaskServerThread(QThread):
    """Thread for running Flask server without blocking the UI."""

    server_started = Signal(int)  # Emits port number
    server_stopped = Signal()
    server_error = Signal(str)

    def __init__(self, config: Config, parent=None):
        super().__init__(parent)
        self.config = config
        self.app = None
        self.server = None
        self.port = config.media_library_port
        self._stop_requested = False

    def find_free_port(self, start_port: int) -> int:
        """
        Find an available port starting from start_port.

        Args:
            start_port: Port to start scanning from

        Returns:
            First available port found

        Raises:
            RuntimeError: If no free port found in range
        """
        for port in range(start_port, start_port + 100):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(("127.0.0.1", port))
                    return port
            except OSError:
                continue
        raise RuntimeError("No free ports available in range")

    def run(self):
        """Run Flask server (blocks until stopped)."""
        try:
            # Find free port
            self.port = self.find_free_port(self.config.media_library_port)

            # Create Flask app with configuration
            config_dict = {
                "books_path": str(self.config.get_books_path() or ""),
                "youtube_path": str(self.config.get_youtube_path() or ""),
                "movies_path": str(self.config.get_movies_path() or ""),
                "tv_shows_path": str(self.config.get_tv_shows_path() or ""),
                "documentaries_path": str(self.config.get_documentaries_path() or ""),
            }

            self.app = create_app(self.config.vault_path, config_dict)

            # Create server using werkzeug
            self.server = make_server(
                "127.0.0.1", self.port, self.app, threaded=True
            )

            # Emit started signal
            self.server_started.emit(self.port)

            # Serve forever until shutdown
            self.server.serve_forever()

        except Exception as e:
            self.server_error.emit(str(e))
        finally:
            self.server_stopped.emit()

    def stop(self):
        """Stop the Flask server gracefully."""
        self._stop_requested = True
        if self.server:
            try:
                # Shutdown must be called from a different thread
                import threading
                shutdown_thread = threading.Thread(target=self.server.shutdown)
                shutdown_thread.daemon = True
                shutdown_thread.start()
                shutdown_thread.join(timeout=1)
            except Exception as e:
                print(f"Error stopping server: {e}")
