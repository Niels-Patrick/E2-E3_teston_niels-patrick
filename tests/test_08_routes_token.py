"""
Tests for the token routes.
"""

import json
from flask_jwt_extended import JWTManager
import pytest
import sys
import os
from src.app.db_manager import init_db, database_uri
from tests.utils import get_refresh_token_by_username

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + "/.."))

from main import create_app  # noqa


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


def test_refresh_tokens(client):
    refresh_token = get_refresh_token_by_username("tuser")

    response = client.get(
            "/api/token/",
            headers={"Authorization": f"Bearer {refresh_token.token}"}
        )
    assert response.status_code == 200

    # Refreshing access token in json file for routes tests
    data = response.get_json()
    token = {
            "access_token": data["access_token"]
        }
    with open("access_token.json", "w") as json_file:
        json.dump(token, json_file)

    response = client.get(
            "/api/token/",
            headers={"Authorization": f"Bearer {data['access_token']}"}
        )
    assert response.status_code == 401


def test_check_token(client):
    with open("access_token.json", "r") as json_file:
        data = json.load(json_file)

    response = client.post(
            "/api/token/",
            json={
                "token": data["access_token"]
            }
        )
    assert response.status_code == 200

    refresh_token = get_refresh_token_by_username("tuser")
    response = client.post(
            "/api/token/",
            json={
                "token": refresh_token.token
            }
        )
    assert response.status_code == 200

    response = client.post(
            "/api/token/",
            json={}
        )
    assert response.status_code == 400
