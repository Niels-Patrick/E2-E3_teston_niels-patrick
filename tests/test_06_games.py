"""
Tests for the Test Request model's methods and functions in the test_request
file.
"""

from flask_jwt_extended import JWTManager
import pytest
import sys
import os
from src.models.games import Game, get_game_by_id, get_games
from src.app.db_manager import init_db, db, database_uri
from tests.utils import create_game
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


@pytest.fixture
def test_user(app):
    return get_user_by_username("tuser")


@pytest.fixture
def game(app, test_user):
    return create_game(db, test_user.id_user)


def test_get_game_by_id(game):
    assert get_game_by_id(game.id_game) == game  # noqa


def test_get_all_games(game):
    games = Game.query.all()

    assert get_games() == games

    db.session.delete(game)
