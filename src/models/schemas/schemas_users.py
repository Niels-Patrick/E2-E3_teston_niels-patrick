"""
Marshmallow Schema for User file.

This file contains the Marshmallow Schema for the User model.
"""

from marshmallow import EXCLUDE, fields
from src.models.users import User
from src.models.schemas.schemas_players import CreatePlayerSchema, \
    UpdatePlayerSchema, ReadPlayerSchema


class CreateUserSchema(CreatePlayerSchema):
    class Meta(CreatePlayerSchema.Meta):
        model = User
        load_instance = True
        include_fk = True
        unknown = EXCLUDE
        exclude = (
            "id_player",
            )

    password = fields.String(required=True)
    email = fields.String(required=True)


class UpdateUserSchema(UpdatePlayerSchema):
    class Meta(UpdatePlayerSchema.Meta):
        model = User
        load_instance = True
        include_fk = True
        unknown = EXCLUDE
        exclude = (
            "id_player",
            )

    password = fields.String()
    email = fields.String()


class ReadUserSchema(ReadPlayerSchema):
    class Meta(ReadPlayerSchema.Meta):
        model = User
        load_instance = True
        include_fk = True

    id_user = fields.UUID()
    password = fields.String()
    email = fields.String()
