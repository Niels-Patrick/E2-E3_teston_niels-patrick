"""
Module to store various utility functions to use mainly in routes functions.

It includes functions to hash passwords and generate tokens.
"""

from datetime import datetime, timezone
from zoneinfo import ZoneInfo
import bcrypt
from flask import request, jsonify
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from src.app.logger_manager import logger_manager


def parse_datetime_string(exp: str) -> datetime:
    """
    Parses Unix timestamp strings to datetime.

    Parameters:
        exp (str): The string to parse.

    Returns:
        dt (datetime): The datetime parsed string.
    """
    try:
        dt = datetime.fromtimestamp(int(exp), timezone.utc)
        logger_manager.info("Datetime string successfully parsed")
        return dt
    except Exception as e:
        logger_manager.error(
            f"Error during datetime string parsing: {str(e)}"
            )
        raise


def check_token_validity(delta: datetime) -> bool:
    """
    Checks the time validity of the token.

    Parameters:
        delta (timedelta): The expiration date of a token.

    Returns:
        True if the token is still valid.
        False if the token has expired.
    """
    try:
        if (delta > datetime.now(ZoneInfo("Europe/Paris"))):
            logger_manager.info("Token is still valid")
            return True

        logger_manager.warning("Token has expired")
        return False
    except Exception as e:
        logger_manager.error(
            f"Error during token validity checking: {str(e)}"
            )
        raise


def get_token_from_header() -> str:
    """
    Fetches a token sent as a request header.

    Returns:
        token (str): An encoded token in case of success.
                     An error message in case of failure.
    """
    try:
        auth_header = request.headers.get('Authorization', None)

        if not auth_header or not auth_header.startswith('Bearer '):
            logger_manager.error("Missing or invalid Authorization header")
            return jsonify({
                "message": "Error: Missing or invalid Authorization header"
                }), 401

        token = auth_header.split()[1]

        logger_manager.info("Token successfully fetched from header")
        return token
    except Exception as e:
        logger_manager.error(
            f"Error while getting token from header: {str(e)}"
            )
        raise


def hash_password(password: str) -> str:
    """
    Hashes a password with salt.

    Parameters:
        password (str): The password to hash.

    Returns:
        hashed_password (str): The hashed password, decoded to store as
                               string in the database.
    """
    try:
        encoded_password = password.encode('utf-8')
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(encoded_password, salt).decode('utf-8')

        logger_manager.info("Password successfully hashed")
        return hashed_password
    except Exception as e:
        logger_manager.error(
            f"Error during password hashing process: {str(e)}"
            )
        raise


def verify_password(plain: str, hashed: str) -> bool:
    """
    Compares a plain password with a hashed password.

    Parameters:
        plain (str): A plain password.
        hashed (str): A hashed password.

    Returns:
        True if the two passwords are the same, else False.
    """
    try:
        result = bcrypt.checkpw(plain.encode('utf-8'), hashed.encode('utf-8'))

        logger_manager.info("Password successfully verified")
        return result
    except Exception as e:
        logger_manager.error(f"Error during password verification: {str(e)}")
        raise


def check_roles(list_roles: list) -> bool:
    """
    Checks if the current user's role is present in a list of roles.

    Parameters:
        list_roles (list): A list of roles' name.

    Returns:
        True if the user's role is present in the list.
        False if not.
    """
    try:
        verify_jwt_in_request()
        identity = get_jwt_identity()

        if identity.get('role') in list_roles:
            logger_manager.info("Authorized role")
            return True

        logger_manager.warning("Unauthorized role")
        return False
    except Exception as e:
        logger_manager.error(f"Error during role checking: {str(e)}")
        raise
