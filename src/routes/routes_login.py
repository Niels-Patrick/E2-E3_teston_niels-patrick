"""
Login routes module.

This file contains all the routes required for authentication management.
"""

from copy import deepcopy
from datetime import timedelta
import uuid
from flask import Blueprint, Response, jsonify, request
from flask_jwt_extended import create_access_token, create_refresh_token, \
    decode_token, jwt_required
from src.models.players import get_player_by_username
from src.models.refresh_token import RefreshToken, \
    get_refresh_token_by_id
from src.utils.functions_routes import get_token_from_header, verify_password
from src.app.logger_manager import logger_manager
from src.app.db_manager import db


# Defining a Blueprint for the login routes
login = Blueprint("login", __name__)


@login.route('/', methods=['POST'])
def submit() -> Response:
    """
    Checks if the sent credentials correspond to a registered user or not.
    ---
    tags:
        - Login
    consumes:
        - application/json
    parameters:
        - in: body
          name: payload
          required: true
          schema:
            type: object
            properties:
                username:
                    type: string
                password:
                    type: string
    responses:
        200:
            description: Returns access token, refresh token, token type and
                         a success message.
        400:
            description: Returns an error message if no data has been provided
                         when calling the route.
        401:
            description: Returns an error message if the credentials are
                         invalid.
        404:
            description: Returns an error message if the user is not found in
                         the database.
    """
    data = request.json

    if not data:
        logger_manager.error("No data provided")
        return jsonify(message="Error: No data provided"), 400

    user = get_player_by_username(data.get("username"))

    if not user:
        logger_manager.error("Invalid credentials")
        return jsonify(message="Error: Invalid credentials"), 404

    if not verify_password(data.get("password"), user.password):
        logger_manager.error("Invalid credentials")
        return jsonify(message="Error: Invalid credentials"), 401

    try:
        user_dict = user.to_json()
        user_dict["type"] = "access"

        access_token = create_access_token(
            identity=str(user.id),
            expires_delta=timedelta(minutes=15),
            additional_claims=user_dict
            )

        refresh_identity = deepcopy(user_dict)
        refresh_identity["type"] = "refresh"
        refresh_token = create_refresh_token(
            identity=str(user.id),
            expires_delta=timedelta(days=7),
            additional_claims=refresh_identity
            )

        # Storing the refresh token in the database.
        token = RefreshToken(refresh_token)

        old_refresh_token = get_refresh_token_by_id(user.id)

        if old_refresh_token is not None:
            db.session.delete(old_refresh_token)

        db.session.add(token)
        db.session.commit()

        logger_manager.info("Authentication successful")
        return jsonify({
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "message": "Success: Authentication successful"
            }), 200
    except Exception as e:
        logger_manager.error(f"Error while login: {str(e)}")
        raise


@login.route("/", methods=['DELETE'])
@jwt_required()
def logout():
    """
    Deletes the current user's refesh token when logging out.
    ---
    tags:
        - Login
    consumes:
        - application/json
    parameters:
        - in: header
          name: Authorization
          required: true
          type: string
          description: JWT access token (e.g., "Bearer <token>")
    responses:
        200:
            description: Returns a success message.
        404:
            description: Returns an error message if the refresh token is not
                         found in the database.
    """
    token = get_token_from_header()

    # Decodes the token, even if it has expired
    access_token = decode_token(token, allow_expired=True)
    refresh_token = get_refresh_token_by_id(
        uuid.UUID(access_token.get('sub'))
        )

    if not refresh_token:
        logger_manager.error("Refresh token not found in database")
        return jsonify(
            message="Error: Refresh token not found in database"
            ), 404

    try:
        db.session.delete(refresh_token)
        db.session.commit()

        logger_manager.info(
            "Refresh token successfully deleted from database"
            )
        return jsonify(
            message="Success: Refresh token successfully deleted"
            ), 200
    except Exception as e:
        logger_manager.error(f"Error while logging out: {str(e)}")
        raise
