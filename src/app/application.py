"""Main module of the Flask API"""

import os
from flask_socketio import SocketIO
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from src.app.config import AppConfig, LoggerConfig
from src.app.logger_manager import LoggerManager
from flasgger import Swagger
from src.app.db_manager import init_db

from src.routes.routes_login import login
from src.routes.routes_token import token
from src.routes.routes_user import user_management
from src.routes.routes_ai import ai_management
from src.routes.routes_game import game_management
from src.routes.routes_role import role_management
from src.routes.routes_monitoring import monitoring_management


class Application:
    """Class representing the Flask API and its services"""

    def __init__(self, config: AppConfig) -> None:
        """
        Initializes the application with its configuration.

        Parameters:
            config (AppConfig): Application configuration.
        """
        self.config: AppConfig = config
        self.flask: Flask = self._create_flask_api()
        self.logger_manager: LoggerManager = LoggerManager(LoggerConfig())
        self.jwt: JWTManager = JWTManager(self.flask)
        self.socketio: SocketIO = SocketIO(
            self.flask,
            async_mode="gevent",
            cors_allowed_origins="*"
        )
        self.swagger: Swagger = Swagger(self.flask, template={
                "info": {
                    "title": "TicTacToe Model Flask API",
                    "description": "The Flask API for the AI model of the TicTacToe app",  # noqa: E501
                    "version": "0.0.1"
                },
                "securityDefinitions": {
                    "Bearer": {
                        "type": "apiKey",
                        "name": "Authorization",
                        "in": "header",
                        "description": "JWT Authorization header using the Bearer scheme."  # noqa: E501
                    }
                },
                "security": [{"Bearer": []}]
            })

        @self.jwt.unauthorized_loader
        def custom_unauthorized(err):
            print(f"No valid access token: {err}")
            return jsonify(message=f"No valid access token: {err}"), 401

        @self.jwt.invalid_token_loader
        def custom_invalid_token(err):
            print(f"Access token is invalid: {err}")
            return jsonify(message=f"Access token is invalid: {err}"), 422

        @self.jwt.expired_token_loader
        def custom_expired_token(_jwt_header, _jwt_payload):
            print("Access token expired.")
            return jsonify({
                    "message": "Access token expired.",
                    "error": "token_expired"
                }), 401

        @self.jwt.revoked_token_loader
        def custom_revoked_token(_jwt_header, _jwt_payload):
            print("Access token revoked.")
            return jsonify({
                    "message": "Access token revoked.",
                    "error": "token_revoked"
                }), 401

    def _create_flask_api(self) -> Flask:
        """
        Creates and configures the Flask instance.

        Returns:
            flask_api (Flask): Configured instance of Flask API.
        """
        # Creating the Flask app
        flask_api: Flask = Flask(
            import_name=self.config.title,
        )

        # JWT Token configuration initialization
        flask_api.config['JWT_TOKEN_LOCATION'] = [os.getenv(
                'JWT_TOKEN_LOCATION'
            )]
        flask_api.config['JWT_HEADER_NAME'] = os.getenv('JWT_HEADER_NAME')
        flask_api.config['JWT_HEADER_TYPE'] = os.getenv('JWT_HEADER_TYPE')
        flask_api.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
        flask_api.config['JWT_ERROR_MESSAGE_KEY'] = 'msg'

        # Registering the Blueprint
        flask_api.register_blueprint(login, url_prefix='/api/login')
        flask_api.register_blueprint(token, url_prefix='/api/token')
        flask_api.register_blueprint(ai_management, url_prefix='/api/ai')
        flask_api.register_blueprint(user_management, url_prefix='/api/user')
        flask_api.register_blueprint(game_management, url_prefix='/api/game')
        flask_api.register_blueprint(role_management, url_prefix='/api/role')
        flask_api.register_blueprint(
            monitoring_management,
            url_prefix='/api/monitoring'
            )

        # Initializing the database
        init_db(flask_api, self.config.database_config.SQLALCHEMY_DATABASE_URI)

        # Enabling CORS for frontend
        CORS(flask_api, supports_credentials=True)

        return flask_api
