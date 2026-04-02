"""
SQLAlchemy Game model file.

This file contains the SQLAlchemy Game model as well as its functions.
"""

from sqlalchemy import Column, DateTime, ForeignKey, String, Date
from sqlalchemy.orm import relationship
import uuid
from sqlalchemy.dialects.postgresql import JSONB, UUID
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
    moves = Column(JSONB, nullable=True)
    id_user_x = Column(
        UUID,
        ForeignKey("users.id_user"),
        nullable=True
        )
    id_user_o = Column(
        UUID,
        ForeignKey("users.id_user"),
        nullable=True
        )
    created_at = Column(
        DateTime(timezone=True),
        server_default=db.func.now(),
        nullable=True
        )

    user_x = relationship(
        "User",
        back_populates="game_x",
        foreign_keys=[id_user_x]
        )

    user_o = relationship(
        "User",
        back_populates="game_o",
        foreign_keys=[id_user_o]
        )

    def __init__(
        self,
        game_date: Date,
        moves: list[str],
        created_at: DateTime = None,
        id_user_x: uuid = None,
        id_user_o: uuid = None,
        game_result: str = None
    ):
        self.game_date = game_date
        self.game_result = game_result
        self.moves = moves
        self.id_user_x = id_user_x
        self.id_user_o = id_user_o
        self.created_at = created_at


def get_games() -> list[Game]:
    """
    Gets a list of all of the games.

    Returns:
        games (list[Game]): a list of all of the games.
    """
    try:
        games = Game.query.all()

        return games
    except Exception as e:
        logger_manager.error(f"Error fetching Games in database: {str(e)}")
        raise


def get_saved_game() -> Game:
    """
    Gets the saved (unfinished) game's data.

    Returns:
        game (Game): the saved game.
    """
    try:
        game = Game.query.filter_by(game_result=None).first()

        return game
    except Exception as e:
        logger_manager.error(f"Error fetching Game in database: {str(e)}")
        raise


def get_last_games(limit: int = 10) -> list[Game]:
    """
    Gets the most recent completed games from the database.

    Returns:
        games (list[Game]): A list of recent games.
    """
    try:
        games = Game.query.filter(Game.game_result.isnot(None))
        games = games.order_by(Game.created_at.desc(), Game.id_game.desc())
        games = games.limit(limit).all()

        return games
    except Exception as e:
        logger_manager.error(
            f"Error fetching last games in database: {str(e)}"
            )
        raise


def get_game_by_id(id: uuid.UUID) -> Game:
    """
    Fetches a specific game from the database based on their id.
    """
    try:
        game = Game.query.filter_by(id_game=id).first()

        logger_manager.info("Game successfully fetched from database")
        return game
    except Exception as e:
        logger_manager.error(f"Error fetching game in database: {str(e)}")
        raise
