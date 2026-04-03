"""
Tests for the ai routes.
"""

import json
from flask_jwt_extended import JWTManager
import pytest
import sys
import os
import torch
from src.ai.game_env import TicTacToe
from src.app.db_manager import init_db, database_uri
from src.utils.model_evaluation import evaluate
from src.ai.brain import Brain

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + "/.."))

from main import create_app  # noqa

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {DEVICE}")


@pytest.fixture
def app():
    app = create_app()
    init_db(app.flask, database_uri)
    jwt = JWTManager(app.flask)  # noqa
    with app.flask.app_context():
        yield app.flask


@pytest.fixture
def client(app):
    return app.test_client()


def test_play_ai_turn(client, monkeypatch):
    class FakeQuery:
        def all(self):
            return []

    env = TicTacToe()

    with open("access_token.json", "r") as json_file:
        data = json.load(json_file)

    response = client.post(
            "/api/ai/",
            json={
                "board": env.board,
                "aiMark": 1
                },
            headers={"Authorization": f"Bearer {data['access_token']}"}
        )
    assert response.status_code == 200
    assert response.get("board") != env.board

    monkeypatch.setattr("src.models.roles.Role.query", FakeQuery())
    payload = {
        "board": [],
        "aiMark": 1
    }
    response = client.post(
            "/api/ai/",
            json=payload,
            headers={"Authorization": f"Bearer {data['access_token']}"}
        )
    assert response.status_code == 400


def test_model_loss_rate():
    """
    Evaluate the real model on 10 games and print a message about retraining
    need.
    """
    # Load the model (assuming best_ttt_model.pt is the latest model)
    try:
        state_dict = torch.load(
            "./best_ttt_model.pt",
            map_location=DEVICE,
            weights_only=True
            )

        model = Brain().to(DEVICE)
        model.load_state_dict(state_dict)
    except Exception as e:
        print(f"Could not load model weights: {e}")
        return

    model.eval()
    results = evaluate(model)
    total_games = results["wins"] + results["losses"] + results["draws"]
    loss_rate = results["losses"] / total_games if total_games else 0.0

    LOSS_RATE_THRESHOLD = 0.75
    if loss_rate >= LOSS_RATE_THRESHOLD:
        print(f"Loss rate is too high ({loss_rate:.2f}), the model needs to be retrained.") # noqa
    else:
        print(
            f"Loss rate is low enough ({loss_rate:.2f}), no need to retrain."
            )
