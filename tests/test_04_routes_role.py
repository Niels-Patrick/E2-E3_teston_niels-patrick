"""
Tests for the role routes.
"""

import json
from flask_jwt_extended import JWTManager
import pytest
import sys
import os
from src.app.db_manager import init_db, database_uri

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


def test_get_roles(client, monkeypatch):
    class FakeQuery:
        def all(self):
            return []

    with open("access_token.json", "r") as json_file:
        data = json.load(json_file)

    response = client.get(
            "/api/role/",
            headers={"Authorization": f"Bearer {data['access_token']}"}
        )
    assert response.status_code == 200

    monkeypatch.setattr("src.models.roles.Role.query", FakeQuery())
    response = client.get(
            "/api/role/",
            headers={"Authorization": f"Bearer {data['access_token']}"}
        )
    assert response.status_code == 404
