"""
Marshmallow Schema for Role file.

This file contains the Marshmallow Schema for the Role model.
"""

from marshmallow import EXCLUDE, fields
from src.models.roles import Role
from src.models.schemas.utils import CamelCaseSQLAlchemyAutoSchema


class CreateRoleSchema(CamelCaseSQLAlchemyAutoSchema):
    class Meta:
        model = Role
        load_instance = True
        unknown = EXCLUDE
        exclude = ("id_role",)

    name = fields.String(required=True)


class UpdateRoleSchema(CamelCaseSQLAlchemyAutoSchema):
    class Meta:
        model = Role
        load_instance = True
        unknown = EXCLUDE
        exclude = ("id_role",)

    name = fields.String()


class ReadRoleSchema(CamelCaseSQLAlchemyAutoSchema):
    class Meta:
        model = Role
        load_instance = True

    id_role = fields.UUID()
    name = fields.String()
