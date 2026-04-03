"""
Player routes module.

This file contains all the routes required to fetch Player objects' data
from the database and to manage CRUD operations.
"""

import os
import uuid
from cryptography.fernet import Fernet
from dotenv import load_dotenv
from flask import Blueprint, Response, jsonify, request
from flask_jwt_extended import get_jwt, jwt_required
from src.app.logger_manager import logger_manager
from src.models.users import User, get_user_by_id, get_user_by_username, \
    get_users
from src.utils.functions_routes import hash_password, verify_password
from src.app.db_manager import db
from src.models.schemas.schemas_users import CreateUserSchema, \
    ReadUserSchema, UpdateUserSchema


# Defining a Blueprint for the User page routes
user_management = Blueprint("user_management", __name__)

load_dotenv()

key = os.getenv("FERN_KEY")
fernet = Fernet(key)
if not fernet:
    logger_manager.error("Error fetching FERN_KEY")
    raise ValueError("FERN_KEY environment variable is not set")


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
        users = get_users()

        if not users:
            return jsonify(message="No users found in database."), 404

        users_dump = ReadUserSchema(
            session=db.session
            ).dump(users)

        return jsonify({
            "users": users_dump,
            "message": "Users list successfully fetched from database."
            }), 200
    except Exception as e:
        logger_manager.error(f"Error while fetching users: {str(e)}")
        raise


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
    user = get_user_by_id(id)

    if not user:
        logger_manager.error("User not found")
        return jsonify(message="Error: User not found"), 404

    try:
        user_dump = ReadUserSchema(
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


@user_management.route('/', methods=['POST'])
def add_user() -> Response:
    """
    Adds a new user to the database.
    ---
    tags:
        - User
    security:
        - Bearer: []
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
                email:
                    type: string
    responses:
        200:
            description: Returns a success message.
        400:
            description: Returns an error message if no payload has been sent
                         in the query.
        409:
            description: Returns an error message if the username is already
                         taken.
    """
    data = request.json

    if not data:
        logger_manager.error("No data provided")
        return jsonify(message="Error: No data provided"), 400

    user = get_user_by_username(data.get("username"))

    if user:
        logger_manager.error("Username already taken")
        return jsonify(message="Error: Username already taken"), 409

    try:
        data['password'] = hash_password(data.get('password'))

        new_user = CreateUserSchema(
            session=db.session
            ).load(data)

        db.session.add(new_user)
        db.session.commit()

        logger_manager.info("User successfully created")
        return jsonify(message="Success: User successfully created"), 200
    except Exception as e:
        logger_manager.error(f"Error while adding a new user: {str(e)}")
        raise


@user_management.route('/', methods=['PUT'])
@jwt_required()
def edit_user() -> Response:
    """
    Updates the user's data in the database.
    ---
    tags:
        - User
    security:
        - Bearer: []
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
                email:
                    type: string
    responses:
        200:
            description: Returns a success message.
        400:
            description: Returns an error message if no payload has been sent
                         in the query.
        404:
            description: Returns an error message if the user and/or their
                         role are not found in the database.
    """
    data = request.json

    if not data:
        logger_manager.error("No data provided")
        return jsonify(message="Error: No data provided"), 400

    # Gets the current user's data based on their ID stored in the token
    access_token = get_jwt()
    current_user: User = get_user_by_id(uuid.UUID(access_token.get("sub")))

    try:
        data['password'] = hash_password(data.get('password'))

        edited_user = UpdateUserSchema().load(  # noqa: F841
            data,
            instance=current_user,
            session=db.session,
            partial=True
            )

        db.session.commit()

        logger_manager.info("User successfully updated")
        return jsonify(
            message="Success: User successfully updated"
            ), 200
    except Exception as e:
        logger_manager.error(
            f"Error while editing user's profile: {str(e)}"
            )
        raise


@user_management.route('/edit-password', methods=['PUT'])
@jwt_required()
def edit_password() -> Response:
    """
    Updates the user's password in the database.
    ---
    tags:
        - User
    security:
        - Bearer: []
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
                old_password:
                    type: string
    responses:
        200:
            description: Returns a success message.
        400:
            description: Returns an error message if no payload has been sent
                         in the query or the old password is incorrect.
        404:
            description: Returns an error message if the user and/or their
                         role are not found in the database.
    """
    data = request.json

    if not data:
        logger_manager.error("No data provided")
        return jsonify(message="Error: No data provided"), 400

    # Gets the current user's data based on their ID stored in the token
    access_token = get_jwt()
    current_user: User = get_user_by_id(uuid.UUID(access_token.get("sub")))

    if not verify_password(data.get("old_password"), current_user.password):
        logger_manager.error("The old password is incorrect")
        return jsonify(message="Error: The old password is incorrect"), 400

    try:
        current_user.password = hash_password(data.get("password"))

        db.session.commit()

        logger_manager.info("Password successfully updated")
        return jsonify(message="Success: Password successfully updated"), 200
    except Exception as e:
        logger_manager.error(f"Error while editing own password: {str(e)}")
        raise


@user_management.route('/<string:username>', methods=["DELETE"])
@jwt_required()
def delete_user(username: str) -> Response:
    """
    Deletes a specific user from the database.
    ---
    tags:
        - User
    security:
        - Bearer: []
    parameters:
        - in: path
          name: username
          type: string
          required: true
          description: The username of the user to delete.
    responses:
        200:
            description: Returns a success message.
        404:
            description: Returns an error message if the user is not found in
                         the database.
    """
    # Gets the current user's data based on their ID stored in the token
    access_token = get_jwt()
    role = access_token.get('role')

    if role['name'] != 'Admin':
        current_user: User = get_user_by_id(access_token.get('sub'))

    if role['name'] == 'Admin':
        current_user: User = get_user_by_username(username)

    if not current_user:
        logger_manager.error("User not found")
        return jsonify(message="Error: User not found"), 404

    try:
        db.session.delete(current_user)
        db.session.commit()

        logger_manager.info("User successfully deleted")
        return jsonify(message="Success: User successfully deleted"), 200
    except Exception as e:
        logger_manager.error(f"Error while deleting user: {str(e)}")
        raise
