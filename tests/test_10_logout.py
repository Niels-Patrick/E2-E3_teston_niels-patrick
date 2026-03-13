"""
Test for the logout route.
"""

import json
from flask_jwt_extended import JWTManager
import pytest
import sys
import os
from src.app.db_manager import init_db, database_uri, db
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


def test_logout(client):
    with open("access_token.json", "r") as json_file:
        data = json.load(json_file)

    user = get_user_by_username("tuser")

    # Correct token
    response = client.delete(
        "/api/login/",
        headers={"Authorization": f"Bearer {data['access_token']}"}
    )
    assert response.status_code == 200

    # Deleting json access_token file
    os.remove("access_token.json")

    # Token not found
    response = client.delete(
        "/api/login/",
        headers={"Authorization": f"Bearer {data['access_token']}"}
    )
    assert response.status_code == 404

    db.session.delete(user)
    db.session.commit()
