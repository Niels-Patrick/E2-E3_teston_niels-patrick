"""
Tests for the Refresh Token model's methods and functions in the refresh_token
file.
"""

import uuid
from src.app.db_manager import init_db, database_uri
from flask_jwt_extended import JWTManager, decode_token
import pytest
import sys
import os
from src.models.refresh_tokens import get_refresh_token, \
    get_refresh_token_by_id
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


def test_to_json(client):
    token = get_refresh_token_by_username("tuser")
    result = {"refresh_token": token.token}

    assert token.to_json() == result


def test_get_refresh_token_by_id(client):
    token = get_refresh_token_by_username("tuser")
    token_decoded = decode_token(token.token)
    token_id = token_decoded.get("sub")

    assert get_refresh_token_by_id('none') == None  # noqa
    assert get_refresh_token_by_id(uuid.UUID(token_id)) == token


def test_get_refresh_token(client):
    token = get_refresh_token_by_username("tuser")

    assert get_refresh_token('none') == None  # noqa
    assert get_refresh_token(token.token) == token
