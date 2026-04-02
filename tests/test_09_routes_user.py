"""
Tests for the user routes.
"""

import json
import uuid
from flask_jwt_extended import JWTManager
import pytest
import sys
import os
from src.app.db_manager import init_db, database_uri
from src.models.users import get_user_by_username

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


def test_add_user(client):
    with open("access_token.json", "r") as json_file:
        data = json.load(json_file)

    user = {
        "username": "utest",
        "password": 'password',
        "email": "user.test@gmail.com",
        "id_role": "c640cf59-9be5-4f54-a72d-62d1327c186b"
    }

    response = client.post(
            "/api/user/",
            json=user,
            headers={"Authorization": f"Bearer {data['access_token']}"}
        )
    assert response.status_code == 200

    response = client.post(
            "/api/user/",
            json={},
            headers={"Authorization": f"Bearer {data['access_token']}"}
        )
    assert response.status_code == 400

    user["username"] = "tuser"
    response = client.post(
            "/api/user/",
            json=user,
            headers={"Authorization": f"Bearer {data['access_token']}"}
        )
    assert response.status_code == 409


def test_get_a_user(client):
    with open("access_token.json", "r") as json_file:
        data = json.load(json_file)

    user = get_user_by_username("utest")
    response = client.get(
            f"/api/user/{user.id_user}",
            headers={"Authorization": f"Bearer {data['access_token']}"}
        )
    assert response.status_code == 200

    response = client.get(
            f"/api/user/{uuid.uuid4()}",
            headers={"Authorization": f"Bearer {data['access_token']}"}
        )
    assert response.status_code == 404


def test_get_users_list(client, monkeypatch):
    class FakeQuery:
        def all(self):
            return []

    with open("access_token.json", "r") as json_file:
        data = json.load(json_file)

    response = client.get(
            "/api/user/",
            headers={"Authorization": f"Bearer {data['access_token']}"}
        )
    assert response.status_code == 200

    monkeypatch.setattr("src.models.users.User.query", FakeQuery())
    response = client.get(
            "/api/user/",
            headers={"Authorization": f"Bearer {data['access_token']}"}
        )
    assert response.status_code == 404


def test_edit_user(client):
    with open("access_token.json", "r") as json_file:
        data = json.load(json_file)

    user = {
        "password": 'password',
        "email": "user.test@gmail.com"
    }

    response = client.put(
            "/api/user/",
            json=user,
            headers={"Authorization": f"Bearer {data['access_token']}"}
        )
    assert response.status_code == 200

    response = client.put(
            "/api/user/",
            json={},
            headers={"Authorization": f"Bearer {data['access_token']}"}
        )
    assert response.status_code == 400


def test_edit_password(client):
    with open("access_token.json", "r") as json_file:
        data = json.load(json_file)

    password_json = {
        "username": "utest",
        "password": "newPassword",
        "old_password": "password"
    }

    response = client.put(
            "/api/user/edit-password",
            json=password_json,
            headers={"Authorization": f"Bearer {data['access_token']}"}
        )
    assert response.status_code == 200

    response = client.put(
            "/api/user/edit-password",
            json={},
            headers={"Authorization": f"Bearer {data['access_token']}"}
        )
    assert response.status_code == 400


def test_delete_user(client):
    with open("access_token.json", "r") as json_file:
        data = json.load(json_file)

    response = client.delete(
            "/api/user/utest",
            headers={"Authorization": f"Bearer {data['access_token']}"}
        )
    assert response.status_code == 200

    response = client.delete(
            "/api/user/utest",
            headers={"Authorization": f"Bearer {data['access_token']}"}
        )
    assert response.status_code == 404
