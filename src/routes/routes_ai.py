"""
AI routes module.

This file contains all the routes required to make requests to the AI model.
"""

import os
from cryptography.fernet import Fernet
from dotenv import load_dotenv
from flask import Blueprint, Response, jsonify, request
from flask_jwt_extended import jwt_required
import numpy as np
import torch
from src.app.logger_manager import logger_manager
from src.ai.brain import Brain
from src.ai.player_wrappers import model_player


DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {DEVICE}")

# Defining a Blueprint for the AI page routes
ai_management = Blueprint("ai_management", __name__)

load_dotenv()

key = os.getenv("FERN_KEY")
fernet = Fernet(key)
if not fernet:
    logger_manager.error("Error fetching FERN_KEY")
    raise ValueError("FERN_KEY environment variable is not set")


@ai_management.route("/", methods=["POST"])
@jwt_required()
def play_ai_turn() -> Response:
    """
    Makes the model play a turn in a given context (a specific board
    configuration).
    ---
    tags:
        - AI
    security:
        - Bearer: []
    responses:
        200:
            description: Returns the new board after the AI played.
    """
    try:
        data = request.json
        board = np.array(data.get("board"))
        board_numeric = np.where(
            board == " ",
            0,
            np.where(board == "X", 1, np.where(board == "O", -1, 0))
            )

        state_dict = torch.load(
            "./best_ttt_model.pt",
            map_location=DEVICE,
            weights_only=True
            )

        model = Brain().to(DEVICE)
        model.load_state_dict(state_dict)

        ai_mark = -1
        if data.get("aiMark") == "X":
            ai_mark = 1
        else:
            ai_mark = -1

        ai_move = model_player(model, board_numeric.copy(), ai_mark, DEVICE)

        board[ai_move] = data.get("aiMark")

        return jsonify({
            "board": board.tolist(),
            "message": "AI move successfully done."
            }), 200
    except Exception as e:
        logger_manager.error(f"Error with AI playing its turn: {str(e)}")
        raise
