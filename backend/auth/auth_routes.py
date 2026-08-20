import re
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from extensions import db, bcrypt
from models import User

auth_bp = Blueprint("auth", __name__)

EMAIL_REGEX = r"^[\w\.-]+@[\w\.-]+\.\w+$"


@auth_bp.route("/signup", methods=["POST"])
def signup():
    """Register a new user account."""
    data = request.get_json(silent=True) or {}

    required = ["name", "username", "email", "password"]
    for field in required:
        if not data.get(field) or not str(data.get(field)).strip():
            return jsonify({"message": f"Field '{field}' is required"}), 400

    name = data["name"].strip()
    username = data["username"].strip().lower()
    email = data["email"].strip().lower()
    password = data["password"]

    if not re.match(EMAIL_REGEX, email):
        return jsonify({"message": "Please provide a valid email address"}), 400

    if len(username) < 3:
        return jsonify({"message": "Username must be at least 3 characters long"}), 400

    if len(password) < 6:
        return jsonify({"message": "Password must be at least 6 characters long"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"message": "An account with this email already exists"}), 409

    if User.query.filter_by(username=username).first():
        return jsonify({"message": "Username is already taken"}), 409

    hashed_pw = bcrypt.generate_password_hash(password).decode("utf-8")
    new_user = User(
        name=name,
        username=username,
        email=email,
        password=hashed_pw
    )

    db.session.add(new_user)
    db.session.commit()

    access_token = create_access_token(identity=str(new_user.id))

    return jsonify({
        "message": "Account created successfully",
        "access_token": access_token,
        "user": new_user.to_dict()
    }), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    """Authenticate existing user and issue JWT."""
    data = request.get_json(silent=True) or {}

    identifier = str(data.get("identifier", "")).strip().lower()
    password = str(data.get("password", ""))

    if not identifier or not password:
        return jsonify({"message": "Username/email and password are required"}), 400

    user = User.query.filter(
        (User.username == identifier) | (User.email == identifier)
    ).first()

    if not user or not bcrypt.check_password_hash(user.password, password):
        return jsonify({"message": "Invalid username/email or password"}), 401

    access_token = create_access_token(identity=str(user.id))

    return jsonify({
        "message": f"Welcome back, {user.name}",
        "access_token": access_token,
        "user": user.to_dict()
    }), 200


@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def get_current_user():
    """Fetch current authenticated user profile."""
    current_user_id = int(get_jwt_identity())
    user = db.session.get(User, current_user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404

    return jsonify({"user": user.to_dict()}), 200
