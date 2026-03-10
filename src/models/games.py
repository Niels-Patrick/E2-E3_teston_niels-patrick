"""
SQLAlchemy Game model file.

This file contains the SQLAlchemy Game model as well as its functions.
"""

from sqlalchemy import Column, ForeignKey, String, Date, Text
from sqlalchemy.orm import relationship
import uuid
from sqlalchemy.dialects.postgresql import UUID
from dataclasses import dataclass
from src.app.db_manager import db
from src.app.logger_manager import logger_manager


@dataclass
class Game(db.Model):
    """SQLAlchemy Game model"""

    __tablename__ = 'games'
    id_game = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    game_date = Column(Date, nullable=True)
    game_result = Column(String(50), nullable=True)
    moves = Column(Text, nullable=True)
    id_event = Column(UUID, ForeignKey("events.id_event"), nullable=True)
    id_opening = Column(UUID, ForeignKey("openings.id_opening"), nullable=True)
    id_player_white = Column(
        UUID,
        ForeignKey("players.id_player"),
        nullable=True
        )
    id_player_black = Column(
        UUID,
        ForeignKey("players.id_player"),
        nullable=True
        )

    event = relationship(
        "Event",
        back_populates="game",
        foreign_keys=[id_event]
        )
    opening = relationship(
        "Opening",
        back_populates="game",
        foreign_keys=[id_opening]
        )
    player_white = relationship(
        "Player",
        back_populates="game_white",
        foreign_keys=[id_player_white]
        )
    player_black = relationship(
        "Player",
        back_populates="game_black",
        foreign_keys=[id_player_black]
        )

    def __init__(
        self,
        game_date: Date,
        game_result: str,
        moves: list[str],
        id_event: uuid,
        id_opening: uuid,
        id_player_white: uuid,
        id_player_black: uuid
    ):
        self.game_date = game_date
        self.game_result = game_result
        self.moves = moves
        self.id_event = id_event
        self.id_opening = id_opening
        self.id_player_white = id_player_white
        self.id_player_black = id_player_black


def get_games() -> list[Game]:
    """
    Gets a list of all of the games.

    Returns:
        games (list[Game]): a list of all of the games.
    """
    try:
        games = db.query(Game).all()

        return games
    except Exception as e:
        logger_manager.error(f"Error fetching Games in database: {str(e)}")
        raise


def get_game_by_id(id: uuid) -> Game:
    """
    Fetches a specific game from the database based on their id.
    """
    try:
        game = Game.query.filter_by(id=id).first()

        logger_manager.info("Game successfully fetched from database")
        return game
    except Exception as e:
        logger_manager.error(f"Error fetching game in database: {str(e)}")
        raise
