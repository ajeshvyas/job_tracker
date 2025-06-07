from flask import Blueprint, request, jsonify, g
from app import db
from app.models import User
from app.utils import hash_password, verify_password, generate_jwt, generate_refresh_token, verify_jwt

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.json
    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"error": "User already exists"}), 400

    user = User(
        email=data["email"],
        password=hash_password(data["password"])
    )
    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "User registered successfully"}), 201

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.json
    user = User.query.filter_by(email=data["email"]).first()
    if not user or not verify_password(data["password"], user.password):
        return jsonify({"error": "Invalid credentials"}), 401

    access_token = generate_jwt(user.id)
    refresh_token = generate_refresh_token(user.id)

    response = jsonify({"message": "Login successful"})
    response.set_cookie("access_token", access_token, httponly=True, secure=True, samesite="Strict")
    response.set_cookie("refresh_token", refresh_token, httponly=True, secure=True, samesite="Strict")
    return response

@auth_bp.route("/refresh", methods=["POST"])
def refresh():
    token = request.cookies.get("refresh_token")
    payload = verify_jwt(token)
    if not payload or payload.get("type") != "refresh":
        return jsonify({"error": "Invalid refresh token"}), 401

    new_access_token = generate_jwt(payload["user_id"])
    response = jsonify({"message": "Access token refreshed"})
    response.set_cookie("access_token", new_access_token, httponly=True, secure=True, samesite="Strict")
    return response

@auth_bp.route("/logout", methods=["POST"])
def logout():
    response = jsonify({"message": "Logged out"})
    response.set_cookie("access_token", "", expires=0)
    response.set_cookie("refresh_token", "", expires=0)
    return response
