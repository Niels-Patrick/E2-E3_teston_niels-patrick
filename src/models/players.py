"""
SQLAlchemy Player model file.

This file contains the SQLAlchemy Player model as well as its functions.
"""

import uuid
from sqlalchemy import Column, String, Integer
from sqlalchemy.dialects.postgresql import UUID
from dataclasses import dataclass
from src.app.db_manager import db
from src.app.logger_manager import logger_manager
from sqlalchemy.orm import relationship


@dataclass
class Player(db.Model):
    """SQLAlchemy Player model"""

    __tablename__ = 'players'
    id_player = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
        )
    username = Column(String(500), nullable=False)
    elo = Column(Integer, nullable=True, default=None)
    type = Column(String(50), nullable=False)

    game_white = relationship(
        "Game",
        back_populates="player_white",
        foreign_keys="Game.id_player_white"
        )
    game_black = relationship(
        "Game",
        back_populates="player_black",
        foreign_keys="Game.id_player_black"
        )

    __mappers_args__ = {
        "polymorphic_on": type,
        "polymorphic_identity": "player"
    }

    def to_json(self) -> dict:
        """
        Returns a user's data as JSON.
        """
        json_user = {
            "id_player": self.id_player,
            "username": self.username
        }

        logger_manager.info("User's information successfully fetched")
        return json_user


def get_players() -> list[Player]:
    """
    Gets a list of all of the players.

    Returns:
        players (list[Player]): a list of all of the players.
    """
    try:
        players = Player.query.all()

        logger_manager.info("Players successfully fetched")
        return players
    except Exception as e:
        logger_manager.error(f"Error fetching players in database: {str(e)}")
        raise


def get_player_by_username(username: str) -> Player:
    """
    Fetches a specific user from the database based on their unique username.
    """
    try:
        player = Player.query.filter_by(username=username).first()

        logger_manager.info("User successfully fetched from database")
        return player
    except Exception as e:
        logger_manager.error(f"Error fetching user in database: {str(e)}")
        raise


def get_player_by_id(id: uuid) -> Player:
    """
    Fetches a specific user from the database based on their unique username.
    """
    try:
        player = Player.query.filter_by(id=id).first()

        logger_manager.info("User successfully fetched from database")
        return player
    except Exception as e:
        logger_manager.error(f"Error fetching user in database: {str(e)}")
        raise
