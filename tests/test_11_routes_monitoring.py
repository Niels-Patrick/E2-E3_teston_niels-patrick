"""
Tests for the ai routes.
"""

from flask_jwt_extended import JWTManager
import pytest
import sys
import os
import torch
from src.app.db_manager import init_db, database_uri

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


def test_metrics(client):
    r = client.get("http://localhost:5000/metrics")

    assert r.status_code == 200
    assert "ttt_win_rate" in r.text


def test_get_last_game_results(client):
    r = client.get("/api/monitoring/last-game-results")

    assert r.status_code == 200


def test_retrain_model(client):
    r = client.post("/api/monitoring/retrain")

    assert r.status_code == 202


def test_health(client):
    r = client.get("/api/monitoring/")

    assert r["status"] == "ok"
