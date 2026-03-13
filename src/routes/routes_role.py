"""
Role routes module.

This file contains all the routes required to fetch Role objects' data from
the database and to manage CRUD operations.
"""

from flask import Blueprint, Response, jsonify
from src.models.roles import get_all_roles
from src.app.logger_manager import logger_manager
from src.utils.rbac_decorator import roles_required

# Defining a Blueprint for the role page routes
role_management = Blueprint("role_management", __name__)


@role_management.route('/', methods=['GET'])
@roles_required(['Admin'])
def get_roles() -> Response:
    """
    Gets all the roles' data from the database.
    ---
    tags:
        - Roles
    security:
        - Bearer: []
    responses:
        200:
            description: Returns a list of roles and a success message.
        404:
            description: Returns an error message if no roles are found in the
                         database.
    """
    roles = get_all_roles()

    if not roles:
        logger_manager.error("No roles found in database")
        return jsonify(message="Error: no roles found."), 404

    try:
        roles_json = [role.to_json() for role in roles]

        logger_manager.info("Roles successfully fetched")
        return jsonify({
            "roles": roles_json,
            "message": "Success: Roles successfully fetched"
            }), 200
    except Exception as e:
        logger_manager.error(f"Error while getting roles: {str(e)}")
        raise
