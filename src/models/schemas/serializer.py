from typing import Union, Any
from src.models.players import Player
from src.models.users import User
from src.models.schemas.schemas_players import CreatePlayerSchema, \
    UpdatePlayerSchema, ReadPlayerSchema
from src.models.schemas.schemas_users import CreateUserSchema, \
    UpdateUserSchema, ReadUserSchema


def serialize_player(obj: Union[Player, User]) -> dict[str, Any]:
    """
    Serialize a Player or User using the correct schema automatically.
    """
    if isinstance(obj, User):
        schema = ReadUserSchema()
    elif isinstance(obj, Player):
        schema = ReadPlayerSchema()
    else:
        raise TypeError(f"Expected Player or User, got {type(obj)}")

    return schema.dump(obj)


def serialize_players(
    players_list: list[Union[Player, User]]
) -> list[dict[str, Any]]:
    """Serialize a list of Player + User using polymorphic logic."""
    return [serialize_player(obj) for obj in players_list]


def serialize_users(users_list: list[User]) -> list[dict[str, Any]]:
    """Serialize a list where all instances are User."""
    schema = ReadUserSchema(many=True)
    return schema.dump(users_list)


def load_player(
    data: dict[str, Any],
    update: bool = False
) -> Union[Player, User]:
    """
    Load a Player or User instance from input dict.
    Chooses correct schema based on data["type"].
    """
    # Determine the type of instance
    obj_type = data.get("type", "player")

    if obj_type == "user":
        schema = UpdateUserSchema() if update else CreateUserSchema()
    else:
        schema = UpdatePlayerSchema() if update else CreatePlayerSchema()

    return schema.load(data)
