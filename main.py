"""
Main entry point for the backend TicTacToe model Flask API.

This file contains the factory function to create the application as well as
the entry point to execute the function.

This file initializes the required configurations and starts the application.

The routes' documentation is available on: http://127.0.0.1:5001/apidocs/
"""

import os
import sys
import eventlet

from src.app.application import Application
from src.app.config import AppConfig


eventlet.monkey_patch()

# Adds the project root to the Python path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)


def create_app() -> Application:
    """
    Factory function to create the application.

    Returns:
        application (Application): Application instance.
    """
    try:
        application = Application(AppConfig())
    except Exception as e:
        print(f"Error while creating application: {str(e)}")
        raise

    return application


# Main entry point
if __name__ == '__main__':
    app = create_app()

    app.socketio.run(
        app.flask,
        host=app.config.network_config.APP_HOST,
        port=app.config.network_config.APP_PORT,
        debug=True
        )
