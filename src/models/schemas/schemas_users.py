"""
Marshmallow Schema for User file.

This file contains the Marshmallow Schema for the User model.
"""

from marshmallow import EXCLUDE, fields
from src.models.schemas.schemas_roles import ReadRoleSchema
from src.models.schemas.utils import CamelCaseSQLAlchemyAutoSchema
from src.models.users import User


class CreateUserSchema(CamelCaseSQLAlchemyAutoSchema):
    class Meta:
        model = User
        load_instance = True
        include_fk = True
        unknown = EXCLUDE
        exclude = (
            "id_user",
            "game_x",
            "game_o",
            "role"
            )

    username = fields.String(required=True)
    password = fields.String(required=True)
    email = fields.String(required=True)
    id_role = fields.UUID(required=True)


class UpdateUserSchema(CamelCaseSQLAlchemyAutoSchema):
    class Meta:
        model = User
        load_instance = True
        include_fk = True
        unknown = EXCLUDE
        exclude = (
            "id_user",
            "game_x",
            "game_o",
            "role"
            )

    username = fields.String()
    password = fields.String()
    email = fields.String()
    id_role = fields.UUID()


class ReadUserSchema(CamelCaseSQLAlchemyAutoSchema):
    class Meta:
        model = User
        load_instance = True
        include_fk = True

    id_user = fields.UUID()
    username = fields.String()
    password = fields.String()
    email = fields.String()
    id_role = fields.UUID()
    game_x = fields.Nested('ReadGameSchema')
    game_o = fields.Nested('ReadGameSchema')
    role = fields.Nested(ReadRoleSchema)
