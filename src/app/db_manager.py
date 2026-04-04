"""
Module to manage the databases connexions.
"""

from src.app.config import DatabaseConfig
from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from src.app.logger_manager import logger_manager


# Initializing SQLAlchemy
db = SQLAlchemy()

database_uri = DatabaseConfig.SQLALCHEMY_DATABASE_URI


def init_db(app: Flask, database_uri: str) -> None:
    """
    Initializes the main database connexion.

    Parameters:
        app (Flask): An instance of the Flask application.
    """
    app.config["SQLALCHEMY_DATABASE_URI"] = database_uri
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    try:
        if app.extensions.get("sqlalchemy") is not None:
            logger_manager.info("Database already initialized for this app")
            return

        db.init_app(app)

        with app.app_context():
            db.reflect()  # Auto-detection of existing tables in DB

        logger_manager.info("Database successfully initialized")
    except Exception as e:
        logger_manager.error(f"Error during DB initialization: {str(e)}")
