"""
Tests for the Role model's methods and functions in the role file.
"""

from flask_jwt_extended import JWTManager
import pytest
import sys
import os
from src.models.roles import Role, get_all_roles, get_role
from src.app.db_manager import init_db, db, database_uri
from tests.utils import create_role, get_role_by_name

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
    role = create_role(db)
    result = {
        "id_role": role.id_role,
        "name": role.name
    }

    assert role.to_json() == result


def test_get_role(client):
    role: Role = get_role_by_name('test')

    assert get_role(role.id_role) == role

    db.session.delete(role)
    db.session.commit()


def test_get_all_roles(client):
    roles = Role.query.all()

    assert get_all_roles() == roles
