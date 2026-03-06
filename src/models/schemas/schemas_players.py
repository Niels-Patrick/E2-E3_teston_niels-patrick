"""
Marshmallow Schema for Player file.

This file contains the Marshmallow Schema for the Player model.
"""

from marshmallow import EXCLUDE, fields
from src.models.players import Player
from src.models.schemas.utils import CamelCaseSQLAlchemyAutoSchema


class CreatePlayerSchema(CamelCaseSQLAlchemyAutoSchema):
    class Meta:
        model = Player
        load_instance = True
        include_fk = True
        unknown = EXCLUDE
        exclude = (
            "id_player",
            )

    username = fields.String(required=True)
    elo = fields.Integer(required=False, allow_none=True)
    type = fields.String(required=True)


class UpdatePlayerSchema(CamelCaseSQLAlchemyAutoSchema):
    class Meta:
        model = Player
        load_instance = True
        include_fk = True
        unknown = EXCLUDE
        exclude = (
            "id_player",
            )

    username = fields.String()
    elo = fields.Integer(required=False, allow_none=True)
    type = fields.String()


class ReadPlayerSchema(CamelCaseSQLAlchemyAutoSchema):
    class Meta:
        model = Player
        load_instance = True
        include_fk = True

    id_player = fields.UUID()
    username = fields.String()
    elo = fields.Integer()
    type = fields.String()
