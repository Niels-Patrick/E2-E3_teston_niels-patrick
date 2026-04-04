"""
Static configuration module of the AI model TicTacToe Flask API

This module defines the 'AppConfig' class regrouping all of the
configuration options of the application : Flask, database and logs.
"""

import os
from urllib.parse import quote
from dotenv import load_dotenv
from dataclasses import dataclass, field


load_dotenv()


@dataclass
class DatabaseConfig:
    """Database configuration for the application"""
    DB_USERNAME = os.getenv("DB_USERNAME")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_NAME = os.getenv("DB_NAME")
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")

    SQLALCHEMY_DATABASE_URI = (
            "postgresql://"
            f"{DB_USERNAME}:{quote(DB_PASSWORD, safe='')}@"
            f"{DB_HOST}:{DB_PORT}/{DB_NAME}"
        )
    print(f"Connection string: {SQLALCHEMY_DATABASE_URI}")

    SQLALCHEMY_TRACK_MODIFICATIONS = False


@dataclass
class NetworkConfig:
    """Network configuration for the application (host and port)"""
    APP_HOST = os.getenv("HOST")
    APP_PORT = os.getenv("PORT")


@dataclass
class LoggerConfig:
    """Logs configuration for the application (level, files, rotation)"""
    log_level: str = "INFO"
    log_file_name: str = "model_tictactoe_flask_api.log"
    log_rotation: str = "10 MB"
    log_retention: str = "1 week"
    log_compression: str = "zip"
    log_encoding: str = "utf-8"


@dataclass
class AppConfig:
    """General configuration for the model TicTacToe API"""
    title: str = "Model TicTacToe API"
    database_config: DatabaseConfig = field(default_factory=DatabaseConfig)
    network_config: NetworkConfig = field(default_factory=NetworkConfig)
    logger_config: LoggerConfig = field(default_factory=LoggerConfig)

    def __post_init__(self) -> None:
        """Simple validation of the configuration"""
        if not self.database_config.SQLALCHEMY_DATABASE_URI:
            raise ValueError("The database URI is required.")
        if not self.title:
            raise ValueError("The application title is required.")
