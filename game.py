from typing import Any
import torch
from src.brain import Brain
from src.player_wrappers import model_player
import numpy as np


DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {DEVICE}")


def print_board(board: Any) -> None:
    """
    Prints the game board in the terminal console.

    :param board: A game board as a 1D array of shape (1, 9).
    :type board: Any
    """
    symbols = {0: ".", 1: "X", -1: "O"}
    rows = [" ".join(symbols[x] for x in board[i*3:(i+1)*3]) for i in range(3)]
    print("\n".join(rows))


def human_move(board: Any) -> int:
    """
    Allows the human player to choose a cell on the board.

    :param board: A game board as a 1D array of shape (1, 9).
    :type board: Any

    :return: The cell number selected by the human player.
    :rtype: int
    """
    while True:
        try:
            move = int(input("Enter cell number (0-8): "))
            if move in np.where(board == 0)[0]:
                return move
            print("Invalid move. Try again.")
        except ValueError:
            print("Please enter a number 0-8.")
            raise


def play_human_vs_ai(model: Any) -> None:
    """
    Runs the Tic Tac Toe game.

    :param model: The AI model to play against.
    :type model: Any
    """
    board = np.zeros(9, dtype=int)
    human_mark = 1  # You play as X
    ai_mark = -1  # AI plays as O

    print("You are X (1st). AI is O (2nd).")
    print_board(board)

    while True:
        # Human move
        move = human_move(board)
        board[move] = human_mark

        if check_end(board):
            break

        # AI move
        ai_move = model_player(model, board.copy(), ai_mark, DEVICE)
        board[ai_move] = ai_mark
        print("\nAI plays:", ai_move)
        print_board(board)

        if check_end(board):
            break


def check_end(board: Any) -> bool:
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
            print("AI wins!")
            print_board(board)
            return True

        if s == 3:
            print("You win!")
            print_board(board)
            return True

    if not np.any(board == 0):
        print("Draw!")
        print_board(board)
        return True

    return False


if __name__ == "__main__":
    state_dict = torch.load(
        "best_ttt_model.pt",
        map_location=DEVICE,
        weights_only=True
        )

    new_state_dict = {}
    for k, v in state_dict.items():
        new_state_dict["model." + k] = v

    model = Brain().to(DEVICE)
    model.load_state_dict(state_dict)

    play_human_vs_ai(model)
