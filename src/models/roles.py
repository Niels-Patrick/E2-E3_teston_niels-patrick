"""
SQLAlchemy Role model file.

This file contains the SQLAlchemy Role model as well as its functions.
"""

from typing import List
import uuid
from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
from dataclasses import dataclass
from src.app.db_manager import db
from src.app.logger_manager import logger_manager
from sqlalchemy.orm import relationship


@dataclass
class Role(db.Model):
    """SQLAlchemy Role model"""

    __tablename__ = 'roles'
    id_role = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(50), nullable=False, unique=True)

    user = relationship(
        "User",
        foreign_keys="User.id_role",
        back_populates="role"
        )

    def __init__(self, name: str) -> None:
        """
        Initializes a Role instance.

        :param name: The role's name.
        :type name: str
        """
        self.name = name

    def to_json(self) -> dict:
        """
        Returns a role's data as JSON.
        """
        json_role = {
            "id_role": self.id_role,
            "name": self.name
        }

        logger_manager.info("Role's information successfully fetched")
        return json_role


def get_role(id: uuid) -> Role:
    """
    Fetches a specific role from the database based on its ID.
    """
    try:
        role = Role.query.filter_by(id_role=id).first()

        logger_manager.info("Role successfully fetched from database")
        return role
    except Exception as e:
        logger_manager.error(f"Error fetching role in database: {str(e)}")
        raise


def get_all_roles() -> List:
    """
    Fetches all roles from the database.
    """
    try:
        roles = Role.query.all()

        logger_manager.info("Roles successfully fetched")
        return roles
    except Exception as e:
        logger_manager.error(f"Error fetching roles in database: {str(e)}")
        raise
