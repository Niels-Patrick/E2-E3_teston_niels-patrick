"""
Test for the login route.
"""

import json
from flask_jwt_extended import JWTManager
import pytest
import sys
import os
from src.app.db_manager import init_db, db, database_uri
from tests.utils import create_user

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


def test_submit(client):
    create_user(db)

    # Correct credentials
    response = client.post(
        "/api/login/",
        json={
            "username": "tuser",
            "password": "password"
        }
    )
    assert response.status_code == 200

    # Saving access token in json file for routes tests
    data = response.get_json()
    token = {
            "access_token": data["access_token"]
        }
    with open("access_token.json", "w") as json_file:
        json.dump(token, json_file)

    # No data sent
    response = client.post("/api/login/", json="")
    assert response.status_code == 400

    # Wrong credentials
    response = client.post(
        "/api/login/",
        json={
            "username": "tuser",
            "password": "wrong_password"
        }
    )
    assert response.status_code == 401

    # User not found
    response = client.post(
        "/api/login/",
        json={
            "username": "wrong_user",
            "password": "password"
        }
    )
    assert response.status_code == 404
