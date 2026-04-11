"""
Tests for the ai routes.
"""

import os
from flask_jwt_extended import JWTManager
import pytest
import sys
import torch
from src.app.db_manager import init_db, database_uri
import time
from src.routes import routes_monitoring

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


@pytest.fixture
def admin_headers(client):
    username = os.getenv("ADMIN_USERNAME", "admin")
    password = os.getenv("ADMIN_PASSWORD", "admin1234")

    response = client.post(
        "/api/login/",
        json={"username": username, "password": password}
    )
    assert response.status_code == 200

    token = response.get_json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_metrics(client):
    r = client.get("http://localhost:5000/api/monitoring/metrics")

    assert r.status_code == 200
    assert "ttt_ai_last_10_win_rate" in r.text


def test_get_last_game_results(client):
    r = client.get("/api/monitoring/last-game-results")

    assert r.status_code == 200


def test_retrain_model_statuses(client, monkeypatch, admin_headers):
    """
    Test retrain-model endpoint for all status codes: 202 (success), 400 (bad
    request), 409 (already running).
    Stops the model training after asserts.
    """
    # Prepare valid payload and token
    headers = admin_headers
    valid_payload = {
        "populationSize": 2,  # keep it small for test
        "gamesPerEval": 2,
        "mutationRate": 0.1,
        "mutationStd": 0.1,
        "generations": 2
    }

    # 1. 400 Bad Request (no data)
    r = client.post("/api/monitoring/retrain-model", headers=headers, json={})
    assert r.status_code == 400

    # 2. 202 Accepted (valid request)
    r = client.post(
        "/api/monitoring/retrain-model",
        headers=headers,
        json=valid_payload
        )
    assert r.status_code == 202

    # 3. 409 Conflict (already running)
    r2 = client.post(
        "/api/monitoring/retrain-model",
        headers=headers,
        json=valid_payload
        )
    assert r2.status_code == 409

    # Stop the training thread for test cleanup
    # (Set training_status to 'idle' and release lock if needed)
    # Wait a bit for the thread to start
    time.sleep(0.5)
    if hasattr(routes_monitoring, 'training_status'):
        routes_monitoring.training_status = "idle"
    if hasattr(routes_monitoring, 'training_lock') and (
        routes_monitoring.training_lock.locked()
    ):
        try:
            routes_monitoring.training_lock.release()
        except RuntimeError:
            pass


def test_health(client):
    r = client.get("/api/monitoring/")

    assert r.get_json()["status"] == "ok"


def test_simulate_high_loss_rate(client, monkeypatch):
    """
    Simulate a high AI loss rate for Prometheus scraping by mocking
    update_last_game_metrics.
    """
    def fake_update_last_game_metrics():
        routes_monitoring.AI_LAST_10_LOSS_RATE.set(1.0)
        routes_monitoring.AI_LAST_10_SHOULD_RETRAIN.set(1)

    monkeypatch.setattr(
        routes_monitoring,
        "update_last_game_metrics",
        fake_update_last_game_metrics
        )

    r = client.get("http://localhost:5000/api/monitoring/metrics")
    assert r.status_code == 200
    assert b'ttt_ai_last_10_should_retrain 1.0' in r.data
