from flask import Blueprint, jsonify, request, g
from app.auth_middleware import require_auth

bp = Blueprint("items", __name__)


def register_routes(app, service, auth_service):
    # ── Auth routes ──────────────────────────────────────────────

    @app.route("/register", methods=["POST"])
    def register():
        data = request.get_json() or {}
        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return jsonify({"error": "Email and password are required"}), 400

        try:
            user = auth_service.register(email, password)
        except ValueError as e:
            return jsonify({"error": str(e)}), 409

        return jsonify(user.to_dict()), 201

    @app.route("/login", methods=["POST"])
    def login():
        data = request.get_json() or {}
        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return jsonify({"error": "Email and password are required"}), 400

        try:
            token = auth_service.login(email, password)
        except ValueError:
            return jsonify({"error": "Invalid email or password"}), 401

        return jsonify({"token": token}), 200

    # ── Item routes (existing behaviour preserved) ───────────────

    @app.route("/items", methods=["POST"])
    def create_item():
        data = request.get_json()
        # If an Authorization header is present, attach user_id
        user_id = None
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ", 1)[1]
            try:
                payload = auth_service.verify_token(token)
                user_id = payload.get("user_id")
            except ValueError:
                pass  # unauthenticated creation is still allowed

        item = service.create_item(data.get("name"), data.get("description"), user_id=user_id)
        return jsonify(item.to_dict()), 201

    @app.route("/items", methods=["GET"])
    def list_items():
        items = service.list_items()
        return jsonify([i.to_dict() for i in items])

    @app.route("/items/<int:item_id>", methods=["GET"])
    def get_item(item_id):
        item = service.get_item(item_id)
        if not item:
            return jsonify({"error": "Not found"}), 404
        return jsonify(item.to_dict())

    @app.route("/items/<int:item_id>", methods=["DELETE"])
    @require_auth(auth_service)
    def delete_item(item_id):
        # Check ownership for 403
        item = service.get_item(item_id)
        if not item:
            return jsonify({"error": "Not found"}), 404

        if item.user_id is not None and item.user_id != g.current_user["user_id"]:
            return jsonify({"error": "Forbidden: you do not own this item"}), 403

        deleted = service.delete_item(item_id)
        if not deleted:
            return jsonify({"error": "Not found"}), 404
        return "", 204