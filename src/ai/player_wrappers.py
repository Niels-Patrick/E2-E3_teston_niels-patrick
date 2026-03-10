"""
Wrapper functions to manage players actions.
"""

import random
import numpy as np
import torch
from src.ai.game_env import check_winner


def random_player(board: np.array, mark: int) -> int:
    """
    Picks a random available move.

    Parameters:
        board (numpy.array): A numpy array of length 9 (the total number of
                             squares).

    Returns:
        move (int): The random move.
    """
    avail = np.where(board == 0)[0]
    move = int(np.random.choice(avail))

    return move


def heuristic_player(board: np.array, mark: int) -> int:
    """
    Simulates a player who always win if possible, always block opponent if
    necessary, otherwise plays randomly.

    :param board: The current board disposition.
    :type board: np.array
    :param mark: The player's mark.
    :type mark: int

    :return: The player's next move.
    :rtype: int
    """
    ran = random.randint(0, 100)

    if ran < 50:
        # 1. Win if possible
        move = find_winning_move(board, mark)
        if move is not None:
            return move

        # 2. Block opponent
        move = find_winning_move(board, -mark)
        if move is not None:
            return move

        # 3. Center
        if board[4] == 0:
            return 4

    # 4. Random
    return random_player(board, mark)


def model_player(model, board, mark, device) -> int:
    """
    Returns a callable that takes (board, mark) and returns an action index.
    Input representation: raw board values (-1, 0, 1) shaped (1, 9).
    Output: model predicts 9 logits; we mask illegal moves and choose argmax.
    """
    with torch.no_grad():
        x = torch.tensor(
            board * mark,
            dtype=torch.float32,
            device=device
            ).unsqueeze(0)
        logits = model(x)[0]
        mask = torch.tensor(board != 0, device=device)
        logits[mask] = -1e9

        return int(torch.argmax(logits).item())


WIN_LINES = [
    (0, 1, 2),
    (3, 4, 5),
    (6, 7, 8),
    (0, 3, 6),
    (1, 4, 7),
    (2, 5, 8),
    (0, 4, 8),
    (2, 4, 6)
]


def find_threat_squares(board: np.array, mark: int) -> set:
    """
    Returns a set of squares that would complete a win for 'mark' on the next
    move.

    :param board: The game's board.
    :type board: np.array
    :param mark: The current player's mark ('O' or 'X').
    :type mark: int

    :return: A set of winning squares.
    :rtype: set
    """
    threats = set()

    for a, b, c in WIN_LINES:
        line = [board[a], board[b], board[c]]

        if line.count(mark) == 2 and line.count(0) == 1:
            if board[a] == 0:
                threats.add(a)
            elif board[b] == 0:
                threats.add(b)
            else:
                threats.add(c)

    return threats


def find_winning_move(board: np.array, mark: int) -> int:
    """
    Looks for a winning move in the current board disposition for a specific
    player.

    :param board: The current disposition of the board.
    :type board: np.array
    :param mark: The mark of the current player.
    :type mark: int

    :return: A winning move or nothing if there are none.
    :rtype: int
    """
    for move in np.where(board == 0)[0]:
        board[move] = mark

        if check_winner(board) == mark:
            board[move] = 0
            return move

        board[move] = 0

    return None
