"""
Module to manage the databases connexions.
"""

import os

from src.app.config import DatabaseConfig
from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from src.app.logger_manager import logger_manager


# Initializing SQLAlchemy
db = SQLAlchemy()

database_uri = DatabaseConfig.SQLALCHEMY_DATABASE_URI


def seed_default_roles() -> None:
    """Ensures the application roles required by the frontend exist."""
    from src.models.roles import Role

    default_role_names = ("Admin", "Player")
    existing_role_names = {
        role.name for role in db.session.query(Role).filter(
            Role.name.in_(default_role_names)
        ).all()
    }

    missing_roles = [
        Role(name=role_name)
        for role_name in default_role_names
        if role_name not in existing_role_names
    ]

    if not missing_roles:
        return

    db.session.add_all(missing_roles)
    db.session.commit()
    logger_manager.info(
        f"Default roles seeded: {', '.join(role.name for role in missing_roles)}"
    )


def seed_default_admin_user() -> None:
    """Ensures a default admin account exists for first login."""
    from src.models.roles import Role
    from src.models.users import User
    from src.utils.functions_routes import hash_password

    admin_username = os.getenv("ADMIN_USERNAME", "admin")
    admin_email = os.getenv("ADMIN_EMAIL", "admin@example.com")
    admin_password = os.getenv("ADMIN_PASSWORD", "admin1234")

    existing_admin_user = db.session.query(User).filter_by(
        username=admin_username
    ).first()
    if existing_admin_user is not None:
        return

    admin_role = db.session.query(Role).filter_by(name="Admin").first()
    if admin_role is None:
        raise ValueError("Admin role must exist before seeding the admin user")

    admin_user = User(
        username=admin_username,
        password=hash_password(admin_password),
        email=admin_email,
        id_role=admin_role.id_role
    )

    db.session.add(admin_user)
    db.session.commit()
    logger_manager.info(
        f"Default admin user seeded: username={admin_username}, email={admin_email}"
    )


def init_db(app: Flask, database_uri: str) -> None:
    """
    Initializes the main database connexion.

    Parameters:
        app (Flask): An instance of the Flask application.
    """
    app.config["SQLALCHEMY_DATABASE_URI"] = database_uri
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    try:
        if app.extensions.get("sqlalchemy") is not None:
            logger_manager.info("Database already initialized for this app")
            return

        db.init_app(app)

        with app.app_context():
            # Import models so SQLAlchemy registers their metadata before
            # attempting to create missing tables.
            from src.models.roles import Role  # noqa: F401
            from src.models.users import User  # noqa: F401
            from src.models.games import Game  # noqa: F401
            from src.models.refresh_tokens import RefreshToken  # noqa: F401

            db.create_all()
            seed_default_roles()
            seed_default_admin_user()

        logger_manager.info("Database successfully initialized")
    except Exception as e:
        logger_manager.error(f"Error during DB initialization: {str(e)}")
