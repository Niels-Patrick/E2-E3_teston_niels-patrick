"""
Game Environment
"""

from typing import Any
import numpy as np


class TicTacToe:
    def __init__(self) -> None:
        # 3x3 board, player 1: 1, player 2: -1, empty: 0
        self.board = np.zeros((3, 3), dtype=np.int8)
        self.current_player = 1
        self.last_move = None

    def clone(self):
        g = TicTacToe()
        g.board = self.board.copy()
        g.current_player = self.current_player
        g.last_move = self.last_move

        return g

    def legal_moves(self) -> list[tuple[int, int]]:
        return [
            (i, j) for i in range(3) for j in range(3) if self.board[i, j] == 0
        ]

    def apply_move(self, move: list) -> None:
        i, j = move
        if self.board[i, j] != 0:
            raise ValueError('Illegal move')

        self.board[i, j] = self.current_player
        self.last_move = move
        self.current_player *= -1

    def is_win(self, player) -> bool:
        b = self.board
        lines = [
            b[0, :],
            b[1, :],
            b[2, :],
            b[:, 0],
            b[:, 1],
            b[:, 2],
            np.diag(b),
            np.diag(np.rot90(b))
        ]

        return any(np.all(line == player) for line in lines)

    def is_draw(self) -> bool:
        return not self.is_win(1) and not self.is_win(-1) and not (
            self.board == 0
            ).any()

    def game_over(self) -> tuple:
        if self.is_win(1):
            return True, 1

        if self.is_win(-1):
            return True, -1

        if self.is_draw():
            return True, 0

        return False, None

    def canonical_board(self) -> Any:
        # Returns a 2x3x3 numpy array: [plane_current_player, plane_opponent]
        cp = (self.board == self.current_player).astype(np.float32)
        op = (self.board == -self.current_player).astype(np.float32)

        return np.stack([cp, op])

    def encode_move(self, move) -> Any:
        i, j = move

        return i * 3 + j

    def decode_move(self, idx) -> tuple:
        return (idx // 3, idx % 3)
