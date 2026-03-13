from datetime import date, timedelta
import uuid
from flask_jwt_extended import create_refresh_token, decode_token
from flask_sqlalchemy import SQLAlchemy
from src.models.roles import Role
from src.models.users import get_user_by_username
from src.models.users import User
from src.models.refresh_tokens import RefreshToken
from src.models.schemas.schemas_users import ReadUserSchema
from src.models.games import Game
from src.utils.functions_routes import hash_password


def create_refresh(
        db: SQLAlchemy,
        username: str
        ) -> list[RefreshToken, uuid.UUID]:
    """
    Creates a test refresh token and stores it in the database.

    :param db: The database session to store the newly created user in.
    :type db: SQLAlchemy
    :param username: The username of the user to create a refresh token for.
    :type username: str

    :return: The newly created test refresh token and the unique UUID of the
             newly created test refresh token.
    :rtype: list[RefreshToken, uuid.UUID]
    """
    user = get_user_by_username(username)
    user_dict = ReadUserSchema(
            session=db.session
            ).dump(user)

    id = uuid.uuid4()

    new_refresh_token = create_refresh_token(
                    identity=str(id),
                    expires_delta=timedelta(days=7),
                    additional_claims=user_dict
                )

    refresh_token = RefreshToken(new_refresh_token)

    db.session.add(refresh_token)
    db.session.commit()

    return refresh_token, id


def create_role(db: SQLAlchemy) -> Role:
    """
    Creates a test role and stores it in the database.

    :param db: The database session to store the newly created user in.
    :type db: SQLAlchemy

    :return: The newly created test role.
    :rtype: Role
    """
    role = Role(name="test")

    db.session.add(role)
    db.session.commit()

    return role


def create_user(db: SQLAlchemy) -> User:
    """
    Creates a test user and stores it in the database.

    :param db: The database session to store the newly created user in.
    :type db: SQLAlchemy

    :return: The newly created test user.
    :rtype: User
    """
    user = User(
        username="tuser",
        password=hash_password('password'),
        email="test.user@gmail.com",
        id_role="e2ca46c0-abc4-4e0d-ac25-06266f17fdcb"
    )

    db.session.add(user)
    db.session.commit()

    return user


def get_refresh_token_by_username(username: str) -> RefreshToken:
    """
    Gets a specific refresh token based on a username.

    :param username: The username of the user to find their token.
    :type username: str

    :return: The refresh token.
    :rtype: RefreshToken
    """
    tokens = RefreshToken.query.all()
    for refresh_token in tokens:
        token = decode_token(refresh_token.token, allow_expired=True)

        if token.get("username") == username:
            return refresh_token


def create_game(
        db: SQLAlchemy,
        user_id: str
        ) -> Game:
    """
    Creates a test "game" and stores it in the database.

    :param db: The database session to store the newly created game in.
    :type db: SQLAlchemy

    :return: The newly created game.
    :rtype: Game
    """
    game = Game(
        game_date=date(2000, 1, 1),
        game_result="0-1",
        moves=[],
        id_user_x=user_id,
        id_user_o=user_id
    )

    db.session.add(game)
    db.session.commit()

    return game


def get_role_by_name(name: str) -> Role:
    """
    Gets a specific refresh token based on a username.

    :param name: The name of the Role object to find.
    :type name: str

    :return: The Role object.
    :rtype: Role
    """
    role = Role.query.filter_by(name=name).first()
    return role
