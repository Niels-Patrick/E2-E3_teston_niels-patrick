"""
Marshmallow Schema for Game file.

This file contains the Marshmallow Schema for the Game model.
"""

from marshmallow import EXCLUDE, fields
from src.models.games import Game
from src.models.schemas.schemas_users import ReadUserSchema
from src.models.schemas.utils import CamelCaseSQLAlchemyAutoSchema


class CreateGameSchema(CamelCaseSQLAlchemyAutoSchema):
    class Meta:
        model = Game
        load_instance = True
        include_fk = True
        unknown = EXCLUDE
        exclude = (
            "id_game",
            "user_x",
            "user_o"
            )

    game_date = fields.Date(required=False, allow_none=True)
    game_result = fields.String(required=True)
    moves = fields.String(required=True)
    id_user_x = fields.UUID(required=False, allow_none=True)
    id_user_o = fields.UUID(required=False, allow_none=True)


class UpdateGameSchema(CamelCaseSQLAlchemyAutoSchema):
    class Meta:
        model = Game
        load_instance = True
        include_relationships = True
        include_fk = True
        unknown = EXCLUDE
        exclude = (
            "id_game",
            "user_x",
            "user_o"
            )

    game_date = fields.Date(required=False, allow_none=True)
    game_result = fields.String()
    moves = fields.String()
    id_user_x = fields.UUID(required=False, allow_none=True)
    id_user_o = fields.UUID(required=False, allow_none=True)


class ReadGameSchema(CamelCaseSQLAlchemyAutoSchema):
    class Meta:
        model = Game
        load_instance = True
        include_relationships = True
        include_fk = True
        unknown = EXCLUDE

    id_game = fields.UUID()
    game_date = fields.Date()
    game_result = fields.String()
    moves = fields.String()
    id_user_x = fields.UUID()
    id_user_o = fields.UUID()
    user_x = fields.Nested(ReadUserSchema)
    user_o = fields.Nested(ReadUserSchema)
