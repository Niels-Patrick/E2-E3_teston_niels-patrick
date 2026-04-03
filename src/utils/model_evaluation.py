"""
Evaluation loop to monitor the model's performance loss and check if a
re-training is needed.
"""

from typing import Any
import numpy as np
import torch
from src.ai.brain import Brain
from src.ai.player_wrappers import heuristic_player, model_player


DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {DEVICE}")


def evaluate(model: Brain) -> dict:
    results = play_games(model, 10)

    return results


def play_games(model: Brain, n: int = 10) -> dict:
    """
    Runs the Tic Tac Toe game.

    :param model: The AI model.
    :type model: Brain
    """
    ai_mark = 1  # AI 1 play as X
    opp_mark = -1  # AI 2 plays as O
    results = {
        "wins": 0,
        "losses": 0,
        "draws": 0
    }

    for _ in range(0, n):
        board = np.zeros(9, dtype=int)

        while True:
            # AI move
            ai_move = model_player(model, board.copy(), ai_mark, DEVICE)
            board[ai_move] = ai_mark
            result = check_end(board)
            if result != "continue":
                break

            # Heuristic player move
            opp_move = heuristic_player(board, opp_mark)
            board[opp_move] = opp_mark
            result = check_end(board)
            if result != "continue":
                break

        match result:
            case "win":
                results["wins"] = results["wins"] + 1
            case "loss":
                results["losses"] = results["losses"] + 1
            case "draw":
                results["draws"] = results["draws"] + 1

    return results


def check_end(board: Any) -> str:
    """
    Checks if the game is over.

    :param board: A game board as a 1D array of shape (1, 9).
    :type board: Any

    :return: The checking result (True = game over, False = game continues).
    :rtype: bool
    """
    b = board.reshape(3, 3)
    lines = []
    lines.extend([b[i, :] for i in range(3)])
    lines.extend([b[:, j] for j in range(3)])
    lines.append(np.diag(b))
    lines.append(np.diag(np.fliplr(b)))

    for line in lines:
        s = np.sum(line)

        if s == -3:
            return "win"

        if s == 3:
            return "loss"

    if not np.any(board == 0):
        return "draw"

    return "continue"
