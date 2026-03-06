from functools import wraps
from typing import Any
from flask import Response, jsonify, request
from flask_jwt_extended import get_jwt, verify_jwt_in_request


def roles_required(allowed_roles: list):
    """
    Decorator factory that creates a decorator that checks if the current
    user's role (stored in their current session token) is present in a list
    of allowed roles. If not, it blocks the access to the route the decorator
    has been applied to.

    Parameters:
        allowed_roles (str): A list of authorized roles.
    """
    def wrapper(fn: Any):
        # Preserves the original function's metadata (name, docstring, ...)
        @wraps(fn)
        def decorator(*args, **kwargs) -> Response | Any:
            verify_jwt_in_request()  # Verifies the validity of the token
            identity = get_jwt()  # Gets user's data from the token
            user_role = identity.get('role')

            if user_role not in allowed_roles:
                return jsonify({"message": "Unauthorized access"}), 403

            return fn(*args, **kwargs)

        return decorator

    return wrapper


def status_required(allowed_statuses: list):
    """
    Decorator factory that creates a decorator that checks if the current test
    request's status is present in a list of allowed statuses. If not, it
    blocks the access to the route the decorator has been applied to.

    Parameters:
        allowed_statuses (str): A list of authorized statuses.
    """
    def wrapper(fn: Any):
        # Preserves the original function's metadata (name, docstring, ...)
        @wraps(fn)
        def decorator(*args, **kwargs) -> Response | Any:
            verify_jwt_in_request()  # Verifies the validity of the token
            data = request.json
            status = data.get("status")

            if status not in allowed_statuses:
                return jsonify({"message": "Unauthorized access"}), 403

            return fn(*args, **kwargs)

        return decorator

    return wrapper
