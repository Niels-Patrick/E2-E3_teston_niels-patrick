"""
Game Environment
"""

import numpy as np


class TicTacToe:
    def __init__(self) -> None:
        # 1 for X, -1 for O and 0 for empty
        self.board = np.zeros(9, dtype=np.int8)
        self.current_player = 1

    def reset(self):
        self.board[:] = 0
        self.current_player = 1

        return self.board.copy()

    def available_moves(self):
        return np.where(self.board == 0)[0]

    def step(self, action) -> None:
        if self.board[action] != 0:
            raise ValueError("Illegal move")

        self.board[action] = self.current_player
        winner = self.check_winner()
        done = (winner is not None) or (not np.any(self.board == 0))
        reward = 0

        if done:
            if winner == 0:  # draw
                reward = 0.5
            else:
                reward = 1.0

        self.current_player *= -1

        return self.board.copy(), reward, done, winner

    def check_winner(self) -> bool:
        b = self.board.reshape(3, 3)
        lines = []
        lines.extend([b[i, :] for i in range(3)])  # rows
        lines.extend([b[:, j] for j in range(3)])  # cols
        lines.append(np.diag(b))
        lines.append(np.diag(np.fliplr(b)))

        # Checking all rows, cols and diags to determine if there is a winner
        for line in lines:
            s = np.sum(line)
            if s == 3:
                return 1  # Player X wins
            if s == -3:
                return -1  # Player O wins

        if not np.any(self.board == 0):
            return 0  # draw

        return None  # Game not finished
