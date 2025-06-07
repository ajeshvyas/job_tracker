from functools import wraps
from flask import request, jsonify, g
from app.utils import verify_jwt
from app.models import User

def jwt_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.cookies.get("access_token")
        if not token:
            return jsonify({"error": "Missing token"}), 401

        payload = verify_jwt(token)
        if not payload or payload.get("type") != "access":
            return jsonify({"error": "Invalid or expired token"}), 401

        user = User.query.get(payload["user_id"])
        if not user:
            return jsonify({"error": "User not found"}), 404

        g.current_user = user
        return f(*args, **kwargs)
    return decorated
