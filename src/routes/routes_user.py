"""
User routes module.

This file contains all the routes required to fetch User objects' data
from the database and to manage CRUD operations.
"""

import uuid
from flask import Blueprint, Response, jsonify
from flask_jwt_extended import jwt_required
from src.app.logger_manager import logger_manager
from src.models.players import get_player_by_id, get_players
from src.models.schemas.schemas_players import ReadPlayerSchema
from src.models.schemas.serializer import serialize_users
from src.app.db_manager import db


# Defining a Blueprint for the User page routes
user_management = Blueprint("user_management", __name__)


@user_management.route('/<uuid:id>', methods=['GET'])
@jwt_required()
def get_a_user(id: uuid) -> Response:
    """
    Fetches a specific user's data from the database.
    ---
    tags:
        - User
    security:
        - Bearer: []
    parameters:
        - in: path
          name: id
          type: uuid
          required: true
          description: The user's uuid.
    responses:
        200:
            description: Returns the user dump (using Marshmallow) and a
                         success message.
        404:
            description: Returns an error message if the user is not found in
                         the database.
    """
    user = get_player_by_id(id)

    if not user:
        logger_manager.error("User not found")
        return jsonify(message="Error: User not found"), 404

    try:
        user_dump = ReadPlayerSchema(
            session=db.session
            ).dump(user)
        logger_manager.info("User's information successfully fetched")
        return jsonify({
            "user": user_dump,
            "message": "Success: Information successfully fetched"
            }), 200
    except Exception as e:
        logger_manager.error(f"Error while getting a specific user: {str(e)}")
        raise


@user_management.route("/", methods=["GET"])
@jwt_required()
def get_all_users() -> Response:
    """
    Gets all the Users' data from the database.
    ---
    tags:
        - Users
    security:
        - Bearer: []
    responses:
        200:
            description: Returns a list of Users and a success message.
        404:
            description: Returns an error message if no Users are found
                         in the database.
    """
    try:
        users = get_players()

        if not users:
            return jsonify(message="No users found in database."), 404

        users_dump = serialize_users(users)

        return jsonify({
            "users": users_dump,
            "message": "Users list successfully fetched from database."
            }), 200
    except Exception as e:
        logger_manager.error(f"Error while fetching users: {str(e)}")
        raise
