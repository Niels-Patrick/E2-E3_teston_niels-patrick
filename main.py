"""
Main entry point for the backend TicTacToe model Flask API.

This file contains the factory function to create the application as well as
the entry point to execute the function.

This file initializes the required configurations and starts the application.

The routes' documentation is available on: http://127.0.0.1:5000/apidocs/
"""

import os
import sys
import threading
from prometheus_client import start_http_server

# Matplotlib is imported indirectly by AI modules; in the container the default
# home directory is not writable for the non-root user.
os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib")

# Adds the project root to the Python path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)

_METRICS_SERVER_STATE = {"started": False}


def start_metrics_server() -> None:
    """Starts Prometheus metrics server once per process."""
    if _METRICS_SERVER_STATE["started"]:
        return

    threading.Thread(
        target=lambda: start_http_server(8000), daemon=True
    ).start()
    _METRICS_SERVER_STATE["started"] = True


def create_app():
    """
    Factory function to create the application.

    Returns:
        application (Application): Application instance.
    """
    from src.app.application import Application
    from src.app.config import AppConfig

    try:
        application = Application(AppConfig())
    except Exception as e:
        print(f"Error while creating application: {str(e)}")
        raise

    return application


# Main entry point
if __name__ == '__main__':
    start_metrics_server()
    app = create_app()

    app.socketio.run(
        app.flask,
        host=app.config.network_config.APP_HOST,
        port=app.config.network_config.APP_PORT,
        debug=True
        )
