"""
SQLAlchemy User model file.

This file contains the SQLAlchemy User model as well as its functions.
"""

import uuid
from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from dataclasses import dataclass
from sqlalchemy.orm import relationship
from src.app.logger_manager import logger_manager
from src.app.db_manager import db


@dataclass
class User(db.Model):
    __tablename__ = 'users'
    id_user = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
        )
    username = Column(String(500), nullable=False)
    password = Column(String(500), nullable=False)
    email = Column(String(250), nullable=False)
    id_role = Column(
        UUID(as_uuid=True),
        ForeignKey('roles.id_role', ondelete="CASCADE"),
        nullable=False
        )

    game_x = relationship(
        "Game",
        back_populates="user_x",
        foreign_keys="Game.id_user_x"
        )

    game_o = relationship(
        "Game",
        back_populates="user_o",
        foreign_keys="Game.id_user_o"
        )

    role = relationship(
        "Role",
        back_populates="user",
        foreign_keys=[id_role]
        )

    def __init__(
            self,
            username: str,
            password: str,
            email: str,
            id_role: UUID
            ):
        self.username = username
        self.password = password
        self.email = email
        self.id_role = id_role


def get_users() -> list[User]:
    """
    Gets a list of all of the users.

    Returns:
        users (list[User]): a list of all of the users.
    """
    try:
        users = User.query.all()

        logger_manager.info("Users successfully fetched")
        return users
    except Exception as e:
        logger_manager.error(f"Error fetching users in database: {str(e)}")
        raise


def get_user_by_username(username: str) -> User:
    """
    Fetches a specific user from the database based on their unique username.
    """
    try:
        user = User.query.filter_by(username=username).first()

        logger_manager.info("User successfully fetched from database")
        return user
    except Exception as e:
        logger_manager.error(f"Error fetching user in database: {str(e)}")
        raise


def get_user_by_id(id: uuid) -> User:
    """
    Fetches a specific user from the database based on their ID.
    """
    try:
        user = User.query.filter_by(id_user=id).first()

        logger_manager.info("User successfully fetched from database")
        return user
    except Exception as e:
        logger_manager.error(f"Error fetching user in database: {str(e)}")
        raise
