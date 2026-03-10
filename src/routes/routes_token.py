"""
Token routes module.

This file contains all the routes required to manage JWT tokens for user
sessions management.
"""

from copy import deepcopy
from datetime import timedelta
import uuid
from flask import Blueprint, Response, jsonify, request
from flask_jwt_extended import decode_token, create_access_token, \
    create_refresh_token
from src.utils.functions_routes import check_token_validity, \
    get_token_from_header, parse_datetime_string
from src.app.logger_manager import logger_manager
from src.models.refresh_tokens import RefreshToken, get_refresh_token_by_id
from src.app.db_manager import db


token = Blueprint("token", __name__)


@token.route('/', methods=['GET'])
def refresh_tokens() -> Response:
    """
    Refreshes an access token using a refresh token, then refreshes the
    refresh token.
    ---
    tags:
        - Token
    responses:
        200:
            description: Returns access token, refresh token, token type and
                         a success message.
        401:
            description: Returns an error message if the token is not of type
                         "refresh".
    """
    token = get_token_from_header()

    try:
        # Decodes the token, even if it has expired
        refresh_token = decode_token(token, allow_expired=True)

        user = {
            "username": refresh_token.get("username")
        }

        token_type = refresh_token.get("type")

        if token_type != "refresh":
            logger_manager.error("Invalid token for refresh")
            return jsonify(message="Error: Invalid token for refresh"), 401

        access_user = deepcopy(user)
        access_user["type"] = "access"
        refresh_user = deepcopy(user)
        refresh_token["type"] = "refresh"

        # Refreshing access token
        new_access_token = create_access_token(
                    identity=str(refresh_token.get("sub")),
                    expires_delta=timedelta(minutes=15),
                    additional_claims=access_user
                    )

        # Refreshing refresh token
        new_refresh_token = create_refresh_token(
                    identity=str(refresh_token.get("sub")),
                    expires_delta=timedelta(days=7),
                    additional_claims=refresh_user
                    )
        new_refresh_token_obj = RefreshToken(new_refresh_token)

        # Adding new refresh token in the database
        db.session.add(new_refresh_token_obj)

        old_refresh_token = get_refresh_token_by_id(
            uuid.UUID(refresh_token.get("sub"))
            )

        # Deleting old refresh token in the database
        db.session.delete(old_refresh_token)

        db.session.commit()

        logger_manager.info("Token refresh successful")
        return jsonify({
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer",
            "message": "Success: Token refresh successful"
            }), 200
    except Exception as e:
        logger_manager.error(f"Error while refreshing the tokens: {str(e)}")
        raise


@token.route('/', methods=['POST'])
def check_token() -> bool:
    """
    Checks the time validity of a token.
    ---
    tags:
        - Token
    consumes:
        - application/json
    parameters:
        - in: body
          name: payload
          required: true
          schema:
            type: object
            properties:
                token:
                    type: string
    responses:
        200:
            description: Returns a boolean response and a success message.
        400:
            description: Returns an error message if no payload has been sent
                         in the query.
    """
    data = request.json

    if not data:
        logger_manager.error("No data provided")
        return jsonify(message="Error: No data provided"), 400

    try:
        payload = decode_token(data.get("token"), allow_expired=True)

        exp = parse_datetime_string(payload.get("exp"))

        response = check_token_validity(exp)

        logger_manager.info("Token checked")
        return jsonify({
            "result": response,
            "message": "Success: Token checked"
            }), 200
    except Exception as e:
        logger_manager.error(f"Error while checking token: {str(e)}")
        raise
