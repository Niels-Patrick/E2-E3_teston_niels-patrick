"""
Logger management module for the TicTacToe model API.

This module provides a logger manager implementation using Loguru with a
singleton pattern.
This module provides static methods to register different levels of logs as
well as a decorator to capture exceptions.
"""

import sys
from pathlib import Path

from loguru import logger

from src.app.config import AppConfig, LoggerConfig


class LoggerManager:
    """
    Logger manager using loguru (singleton pattern).

    Allows the registration of logs messages to the console and a file, with
    rotation, compression and centralized management through AppConfig.
    """

    _instance = None
    _logs_dir: Path = None

    def __new__(cls, config: LoggerConfig) -> "LoggerManager":
        """Implements the singleton pattern"""
        if cls._instance is None:
            instance = super(LoggerManager, cls).__new__(cls)
            cls._instance = instance
            instance._initialize(config)
        return cls._instance

    @classmethod
    def reset_instance(cls):
        """
        Re-initializes the singleton instance.

        Useful for testing or manual re-initialization.
        """
        cls._instance = None

    def _initialize(self, config: LoggerConfig) -> None:
        """
        Initializes the logger with the provided configuration.

        Parameters:
            config (LoggerConfig): Configuration containing logger's
                                   parameters.
        """
        try:
            # Logs folder: logs
            base_path = Path(__file__).resolve().parent.parent
            self._logs_dir = base_path / "logs"
            self._logs_dir.mkdir(parents=True, exist_ok=True)

            # Previous handlers deletion
            logger.remove()

            # Log to console (colorized)
            logger.add(sys.stderr, level=config.log_level)

            logger.info("Logger initialized with config from AppConfig.")
        except Exception as e:
            logger.error(f"Logger initialization failed: {str(e)}")
            raise

    @property
    def logs_dir(self) -> Path:
        """
        Returns the logs folder path.

        Returns:
            path (Path): Folder where the log files are stored.
        """
        path = self._logs_dir

        return path

    @staticmethod
    def info(message: str) -> None:
        """Logs an information message"""
        logger.info(message)

    @staticmethod
    def error(message: str) -> None:
        """Logs an error message"""
        logger.error(message)

    @staticmethod
    def success(message: str) -> None:
        """Logs a success message"""
        logger.success(message)

    @staticmethod
    def debug(message: str) -> None:
        """Logs a debug message"""
        logger.debug(message)

    @staticmethod
    def warning(message: str) -> None:
        """Logs a warning message"""
        logger.warning(message)

    @staticmethod
    def catch(*args, **kwargs) -> callable:
        """
        Returns a decorator to capture exeptions with loguru.

        Return:
            caller (callable): Function decorator
        """
        caller = logger.catch(*args, **kwargs)

        return caller

    def __repr__(self) -> str:
        return f"<LoggerManager logs_dir={self.logs_dir}>"


config = AppConfig()
logger_manager = LoggerManager(config.logger_config)
