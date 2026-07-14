from functools import wraps
from flask import request, jsonify, g


def require_auth(auth_service):
    """Factory that returns a decorator. Reads Bearer token, verifies it,
    attaches the current user payload to flask.g.current_user."""

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            auth_header = request.headers.get("Authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                return jsonify({"error": "Missing or invalid Authorization header"}), 401

            token = auth_header.split(" ", 1)[1]
            try:
                payload = auth_service.verify_token(token)
            except ValueError as e:
                return jsonify({"error": str(e)}), 401

            g.current_user = payload
            return f(*args, **kwargs)

        return decorated_function
    return decorator
