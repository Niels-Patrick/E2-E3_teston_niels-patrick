"""
Tests for the test request routes.
"""

import json
import uuid
from flask_jwt_extended import JWTManager
import pytest
import sys
import os
from src.app.db_manager import init_db, database_uri, db
from src.models.games import Game
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


def test_add_game(client):
    with open("access_token.json", "r") as json_file:
        data = json.load(json_file)

    game = {
        "gameDate": "2000-01-01",
        "gameResult": "0-1",
        "moves": "",
        "idUserX": get_user_by_username("tuser").id_user,
        "idUserO": get_user_by_username("tuser").id_user
    }

    response = client.post(
            "/api/game/",
            json=game,
            headers={"Authorization": f"Bearer {data['access_token']}"}
        )
    assert response.status_code == 200

    response = client.post(
            "/api/game/",
            json={},
            headers={"Authorization": f"Bearer {data['access_token']}"}
        )
    assert response.status_code == 400


def test_get_game(client):
    game: Game = Game.query.filter_by(
        id_user_x=get_user_by_username("tuser").id_user
        ).first()

    with open("access_token.json", "r") as json_file:
        data = json.load(json_file)

    response = client.get(
        f"/api/game/{game.id_game}",
        headers={"Authorization": f"Bearer {data['access_token']}"}
    )
    assert response.status_code == 200

    response = client.get(
        f"/api/game/{uuid.uuid4()}",
        headers={"Authorization": f"Bearer {data['access_token']}"}
    )
    assert response.status_code == 404


def test_get_games_list(client, monkeypatch):
    with open("access_token.json", "r") as json_file:
        data = json.load(json_file)

    response = client.get(
        "/api/game/",
        headers={"Authorization": f"Bearer {data['access_token']}"}
    )
    assert response.status_code == 200


def test_edit_game(client):
    with open("access_token.json", "r") as json_file:
        data = json.load(json_file)

    game: Game = Game.query.filter_by(
        id_user_x=get_user_by_username("tuser").id_user
        ).first()
    game_id = game.id_game

    game = {
        "idGame": game_id,
        "gameDate": "2002-01-01",
        "gameResult": "1-0",
        "moves": "",
        "idUserX": get_user_by_username("tuser").id_user,
        "idUserO": get_user_by_username("tuser").id_user
    }

    response = client.put(
            "/api/game/",
            json=game,
            headers={"Authorization": f"Bearer {data['access_token']}"}
        )
    assert response.status_code == 200

    response = client.put(
            "/api/game/",
            json={},
            headers={"Authorization": f"Bearer {data['access_token']}"}
        )
    assert response.status_code == 400

    game["idGame"] = uuid.uuid4()
    response = client.put(
            "/api/game/",
            json=game,
            headers={"Authorization": f"Bearer {data['access_token']}"}
        )
    assert response.status_code == 404


def test_delete_game(client):
    with open("access_token.json", "r") as json_file:
        data = json.load(json_file)

    game: Game = Game.query.filter_by(
        id_user_x=get_user_by_username("tuser").id_user
        ).first()

    db.session.commit()
    response = client.delete(
            f"/api/game/{game.id_game}",
            headers={"Authorization": f"Bearer {data['access_token']}"}
        )
    assert response.status_code == 200

    response = client.delete(
            f"/api/game/{uuid.uuid4()}",
            headers={"Authorization": f"Bearer {data['access_token']}"}
        )
    assert response.status_code == 404
