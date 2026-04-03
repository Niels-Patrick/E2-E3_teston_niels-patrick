"""
Game routes module.

This file contains all the routes required to fetch Game objects' data
from the database and to manage CRUD operations.
"""

import os
import uuid
from cryptography.fernet import Fernet
from dotenv import load_dotenv
from flask import Blueprint, Response, jsonify, request
from flask_jwt_extended import jwt_required
from src.models.games import Game, get_game_by_id, get_games, get_saved_game
from src.app.logger_manager import logger_manager
from src.models.schemas.schemas_games import CreateGameSchema, \
    ReadGameSchema, UpdateGameSchema
from src.app.db_manager import db
from src.routes.routes_monitoring import update_last_game_metrics
from src.utils.rbac_decorator import roles_required


# Defining a Blueprint for the Game page routes
game_management = Blueprint("game_management", __name__)

load_dotenv()

key = os.getenv("FERN_KEY")
fernet = Fernet(key)
if not fernet:
    logger_manager.error("Error fetching FERN_KEY")
    raise ValueError("FERN_KEY environment variable is not set")


@game_management.route("/", methods=["GET"])
@jwt_required()
def get_all_games() -> Response:
    """
    Gets all the Games' data from the database.
    ---
    tags:
        - Games
    security:
        - Bearer: []
    responses:
        200:
            description: Returns a list of Games and a success message.
        404:
            description: Returns an error message if no Games are found
                         in the database.
    """
    try:
        games = get_games()

        if not games:
            return jsonify(message="No games found in database."), 404

        games_dump = ReadGameSchema(
                session=db.session,
                many=True
            ).dump(games)

        logger_manager.info("Games list successfully fetched from database")
        return jsonify({
            "games": games_dump,
            "message": "Games list successfully fetched from database"
            }), 200
    except Exception as e:
        logger_manager.error(f"Error while fetching games: {str(e)}")
        raise


@game_management.route('/last-game', methods=['GET'])
@jwt_required()
def get_last_game() -> Response:
    """
    Loads the saved game's data from the database.
    ---
    tags:
        - Games
    security:
        - Bearer: []
    parameters:
        - in: path
          name: id
          type: uuid
          required: true
          description: The game's uuid.
    responses:
        200:
            description: Returns the game dump (using Marshmallow) and a
                         success message.
        404:
            description: Returns an error message if the game is not found in
                         the database.
    """
    game = get_saved_game()

    if not game:
        logger_manager.error("No saved game")
        return jsonify({
            "game": None,
            "message": "Sucess: No saved game"
            }), 200

    try:
        game_dump = ReadGameSchema(
            session=db.session
            ).dump(game)
        logger_manager.info("Game's information successfully fetched")
        return jsonify({
            "game": game_dump,
            "message": "Success: Game's information successfully fetched"
            }), 200
    except Exception as e:
        logger_manager.error(f"Error while getting a specific game: {str(e)}")
        raise


@game_management.route('/', methods=['POST'])
@jwt_required()
def add_game() -> Response:
    """
    Adds a new game to the database.
    ---
    tags:
        - Game
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
                game_date:
                    type: date
                game_result:
                    type: date
                moves:
                    type: list of dictionnaries
                id_user_x:
                    type: UUID
                id_user_o:
                    type: UUID
    responses:
        200:
            description: Returns a success message.
        400:
            description: Returns an error message if no payload has been sent
                         in the query.
    """
    data = request.json

    if not data:
        logger_manager.error("No data provided")
        return jsonify(message="Error: No data provided"), 400

    try:
        new_game = CreateGameSchema(
            session=db.session
            ).load(data)

        db.session.add(new_game)
        db.session.commit()

        try:
            update_last_game_metrics()
        except Exception as e:
            logger_manager.error(
                f"Failed to update metrics after adding a game: {str(e)}"
                )

        logger_manager.info("Game successfully created")
        return jsonify(message="Success: Game successfully created"), 200
    except Exception as e:
        logger_manager.error(f"Error while adding a new game: {str(e)}")
        raise


@game_management.route('/', methods=['PUT'])
@jwt_required()
def edit_game() -> Response:
    """
    Updates the game's data in the database.
    ---
    tags:
        - Game
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
                game_date:
                    type: date
                game_result:
                    type: date
                moves:
                    type: list of dictionnaries
                id_user_x:
                    type: UUID
                id_user_o:
                    type: UUID
    responses:
        200:
            description: Returns a success message.
        400:
            description: Returns an error message if no payload has been sent
                         in the query.
        404:
            description: Returns an error message if the game is not found in
                         the database.
    """
    data = request.json

    if not data:
        logger_manager.error("No data provided")
        return jsonify(message="Error: No data provided"), 400

    # Gets the current game's data based on its ID
    current_game: Game = get_game_by_id(uuid.UUID(data.get("idGame")))

    if not current_game:
        logger_manager.error("Current game not found")
        return jsonify(
            message="Error: Current game not found"
            ), 404

    try:
        edited_game = UpdateGameSchema().load(  # noqa: F841
            data,
            instance=current_game,
            session=db.session,
            partial=True
            )

        db.session.commit()

        try:
            update_last_game_metrics()
        except Exception as e:
            logger_manager.error(
                f"Failed to update metrics after editing a game: {str(e)}"
                )

        logger_manager.info("Game successfully updated")
        return jsonify(
            message="Success: Game successfully updated"
            ), 200
    except Exception as e:
        logger_manager.error(
            f"Error while editing game: {str(e)}"
            )
        raise


@game_management.route('/', methods=["DELETE"])
@roles_required(['Admin'])
def delete_games() -> Response:
    """
    Deletes a specific game from the database.
    ---
    tags:
        - Game
    security:
        - Bearer: []
    parameters:
        - in: path
          name: game_id
          type: string
          required: true
          description: The game's unique ID.
    responses:
        200:
            description: Returns a success message.
        404:
            description: Returns an error message if the game is not found in
                         the database.
    """
    all_games = get_all_games()

    if not all_games:
        logger_manager.error("Games not found")
        return jsonify(message="Error: Games not found"), 404

    try:
        for game in all_games:
            db.session.delete(game)
            db.session.commit()

        logger_manager.info("Game successfully deleted")
        return jsonify(message="Success: Game successfully deleted"), 200
    except Exception as e:
        logger_manager.error(f"Error while deleting game: {str(e)}")
        raise
