"""
Game Environment
"""

import numpy as np


class TicTacToe:
    def __init__(self) -> None:
        self.board = np.zeros(9, dtype=np.int8)

    def reset(self):
        self.board[:] = 0

        return self.board.copy()

    def available_moves(self):
        return np.where(self.board == 0)[0]


def check_winner(board: np.array) -> int:
    b = board.reshape(3, 3)
    lines = []
    lines.extend(b)
    lines.extend(b.T)
    lines.append(np.diag(b))
    lines.append(np.diag(np.fliplr(b)))

    # Checking all rows, cols and diags to determine if there is a winner
    for line in lines:
        s = line.sum()
        if s == 3:
            return 1  # Player X wins
        if s == -3:
            return -1  # Player O wins

    if not np.any(board == 0):
        return 0  # draw

    return None  # Game not finished
