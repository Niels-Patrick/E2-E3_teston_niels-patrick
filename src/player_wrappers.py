"""
Wrapper functions to manage players actions.
"""

import numpy as np


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


def heuristic_player(board: np.array, mark: int):
    if board[4] == 0:
        return 4

    return random_player(board, mark)


def model_player_factory(model):
    """
    Returns a callable that takes (board, mark) and returns an action index.
    Input representation: raw board values (-1, 0, 1) shaped (1, 9).
    Output: model predicts 9 logits; we mask illegal moves and choose argmax.
    """
    def player(board, mark):
        """
        Board is from current game view: 1 for X, -1 for O.
        To keep model consistent we feed the board * mark, so the model always
        sees itself as +1.
        """
        input = (board * mark).astype(np.float32).reshape(1, 9)
        logits = model.predict(input, verbose=0)[0]  # shape (9,)
        # Masks illegal moves
        illegal = board != 0
        logits[illegal] = -1e9
        move = int(np.argmax(logits))

        return move

    return player
