"""
Tests for the User model's methods and functions in the user file.
"""

from flask_jwt_extended import JWTManager
import pytest
import sys
import os
from src.models.users import User, get_users, get_user_by_id, \
    get_user_by_username
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


def test_get_user(client):
    user = get_user_by_username("tuser")

    assert get_user_by_id(user.id) == user


def test_get_user_by_username(client):
    user = get_user_by_username("tuser")

    assert get_user_by_username("tuser") == user


def test_get_all_users(client):
    users = User.query.all()

    assert get_users() == users
