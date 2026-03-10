"""
SQLAlchemy Refresh Token model file.

This file contains the SQLAlchemy Refresh Token model as well as its
functions.
"""

import uuid
from flask_jwt_extended import decode_token
from sqlalchemy import UUID, Column, Text
from src.app.logger_manager import logger_manager
from src.app.db_manager import db


class RefreshToken(db.Model):
    """SQLAlchemy RefreshToken model"""

    __tablename__ = 'refresh_tokens'
    id_token = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    token = Column(Text, nullable=False)

    def __init__(self, token: str) -> None:
        """
        Initializes a RefreshToken instance.

        :param token: A refresh token containing a specific user's data.
        :type token: str
        """
        self.token = token

    def to_json(self) -> dict:
        """
        Returns a role's data as JSON.
        """
        json_user = {
            "refresh_token": self.token
        }

        logger_manager.info("Role's information successfully fetched")
        return json_user


def get_refresh_token_by_id(id: uuid.UUID) -> RefreshToken:
    """
    Fetches a specific refresh token from the database based on the user ID
    stored in the payload.

    :param id: The user's ID stored in the token.
    :type id: uuid.UUID

    :return: The refresh token of the current session's user.
    :rtype: RefreshToken
    """
    try:
        refresh_token_list = RefreshToken.query.all()
        for refresh_token in refresh_token_list:
            token = decode_token(refresh_token.token, allow_expired=True)
            logger_manager.info(f"{uuid.UUID(token.get('sub'))} == {id}")

            if uuid.UUID(token.get("sub")) == id:
                logger_manager.info(
                    "Refresh token successfully fetched from database"
                    )
                return refresh_token

        logger_manager.warning("No corresponding refresh token found")
        return None
    except Exception as e:
        logger_manager.error(
            f"Error fetching refresh token in database: {str(e)}"
            )
        raise


def get_refresh_token(token: str) -> RefreshToken:
    """
    Checks if a refresh token exists in the database.

    :param token: The refresh token to check.
    :type token: str

    :return: True if the token exists in the database, False if it doesn't.
    :rtype: RefreshToken
    """
    try:
        refresh_token_list = RefreshToken.query.all()

        for refresh_token in refresh_token_list:
            if token == refresh_token.token:
                logger_manager.info(
                        "Refresh token exists in database"
                    )
                return refresh_token

        logger_manager.warning("Refresh token doesn't exist in database")
        return None
    except Exception as e:
        logger_manager.error(f"Error during refresh token check: {str(e)}")
        raise
