"""
Tests for the ai routes.
"""

from flask_jwt_extended import JWTManager
import pytest
import sys
import os
import torch
from monitoring.model_evaluation import evaluate
from src.ai.brain import Brain
from src.app.db_manager import init_db, database_uri
import requests

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


def test_evaluate(client):
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

    results = evaluate(model)
    total = results["win_rate"] + results["loss_rate"] + results["draw_rate"]

    assert total == 1


def test_metrics_endpoint():
    r = requests.get("http://localhost:8000/metrics")
    assert r.status_code == 200
    assert "ttt_win_rate" in r.text


def test_prometheus_scraping():
    r = requests.get("http://localhost:9090/api/v1/query",
                     params={"query": "ttt_win_rate"})
    data = r.json()

    assert data["status"] == "success"
