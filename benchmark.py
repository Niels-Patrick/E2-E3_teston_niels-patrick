from typing import Any
import numpy as np
import torch
from src.brain import Brain
from src.player_wrappers import heuristic_player, model_player, random_player


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


def check_end(board: Any) -> int:
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

        if s == 3:
            # print("AI wins!")
            # print_board(board)
            return 1

        if s == -3:
            # print("Opponent wins!")
            # print_board(board)
            return -1

    if not np.any(board == 0):
        # print("Draw!")
        # print_board(board)
        return 0

    return None


def play_game(model: Any, opponent_fn: str) -> None:
    """
    Runs the Tic Tac Toe game.

    :param model: The AI model to play against.
    :type model: Any
    """
    board = np.zeros(9, dtype=int)
    opponent_mark = -1  # Opponent plays as O
    ai_mark = 1  # AI plays as X

    # print("AI is X (1st). Opponent is O (2nd).")
    # print_board(board)

    while True:
        # AI move
        ai_move = model_player(model, board.copy(), ai_mark, DEVICE)
        board[ai_move] = ai_mark
        # print("\nAI plays:", ai_move)
        # print_board(board)

        result = check_end(board)
        if result is not None:
            return result

        # Opponent move
        if opponent_fn == "heuristic":
            move = heuristic_player(board, opponent_mark)
        elif opponent_fn == "model":
            move = model_player(model, board, opponent_mark, DEVICE)
        else:
            move = random_player(board, opponent_mark)
        board[move] = opponent_mark

        result = check_end(board)
        if result is not None:
            return result


def benchmark(model_a: Any, opponent_fn: Any, n_games: int = 1000) -> dict:
    wins = 0
    losses = 0
    draws = 0

    for i in range(n_games):
        result = play_game(model_a, opponent_fn)

        if result == 1:
            wins += 1
        elif result == -1:
            losses += 1
        else:
            draws += 1

    return {
        "win_rate": wins / n_games,
        "loss_rate": losses / n_games,
        "draw_rate": draws / n_games
    }


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

    result = benchmark(model, "random")
    print(f"Random opponent: {result}")

    result = benchmark(model, "heuristic")
    print(f"Heuristic opponent: {result}")

    result = benchmark(model, "model")
    print(f"Best saved model opponent: {result}")
