"""
This file stores some utilities functions and classes for Marshmallow schemas.
"""


from marshmallow import EXCLUDE, post_dump, pre_load
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
import re


def camel_case(variable: str) -> str:
    """
    Converts a snake case variable name into camel case.

    Parameters:
        variable (str): The variable name to convert.

    Returns:
        The camel case converted variable name.
    """
    parts = variable.split('_')

    return parts[0] + ''.join(word.capitalize() for word in parts[1:])


def snake_case(variable: str) -> str:
    """
    Converts a camel case variable name into snake case.

    Parameters:
        variable (str): The variable name to convert.

    Returns:
        The snake case converted variable name.
    """
    return re.sub(r'(?<!^)(?=[A-Z])', '_', variable).lower()


class CamelCaseSQLAlchemyAutoSchema(SQLAlchemyAutoSchema):
    """
    Base Marshmallow class to use to convert all variable names from snake
    case to camel case in case of serialization or from camel case to snake
    case in case of deserialization.
    """
    class Meta:
        unknown = EXCLUDE

    @pre_load
    def from_camel_case(self, data, **kwargs):
        if isinstance(data, list):
            return [
                {snake_case(key): value for key, value in item.items()}
                for item in data
            ]
        else:
            return {snake_case(key): value for key, value in data.items()}

    @post_dump
    def to_camel_case(self, data, **kwargs):
        if isinstance(data, list):
            return [
                {camel_case(key): value for key, value in item.items()}
                for item in data
            ]
        else:
            return {camel_case(key): value for key, value in data.items()}
