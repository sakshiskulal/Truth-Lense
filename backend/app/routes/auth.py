from datetime import datetime, timedelta, timezone
import os

from flask import Blueprint, jsonify, request
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from pymongo.errors import PyMongoError, ServerSelectionTimeoutError

from app.utils.db import get_users_collection


bp = Blueprint("auth", __name__)


def _jwt_secret() -> str:
    return os.getenv("JWT_SECRET", os.getenv("SECRET_KEY", "dev-key-deepfake-ai"))


def _jwt_exp_minutes() -> int:
    try:
        return int(os.getenv("JWT_EXPIRES_IN_MINUTES", "60"))
    except ValueError:
        return 60


def _create_token(email: str):
    payload = {
        "sub": email,
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + timedelta(minutes=_jwt_exp_minutes()),
    }
    token = jwt.encode(payload, _jwt_secret(), algorithm="HS256")
    # pyjwt>=2 returns string
    return token


@bp.route("/auth/signup", methods=["POST"])
def signup():
    data = request.get_json(silent=True) or {}
    if not data:
        data = request.form.to_dict() if request.form else {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not email or not password:
        return jsonify({"detail": "Email and password are required"}), 400
    if len(password) < 6:
        return jsonify({"detail": "Password must be at least 6 characters"}), 400

    try:
        users = get_users_collection()
        # Ensure index on email unique
        try:
            users.create_index("email", unique=True)
        except Exception:
            pass

        existing = users.find_one({"email": email})
    except (ServerSelectionTimeoutError, PyMongoError) as e:
        return jsonify({"detail": "Database unavailable", "error": str(e)}), 503
    if existing:
        return jsonify({"detail": "Email already registered"}), 409

    password_hash = generate_password_hash(password)
    user_doc = {
        "email": email,
        "password_hash": password_hash,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }
    try:
        users.insert_one(user_doc)
    except (ServerSelectionTimeoutError, PyMongoError) as e:
        return jsonify({"detail": "Database unavailable", "error": str(e)}), 503

    token = _create_token(email)
    return jsonify({"access_token": token, "token_type": "bearer"}), 201


@bp.route("/auth/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    if not data:
        data = request.form.to_dict() if request.form else {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not email or not password:
        return jsonify({"detail": "Email and password are required"}), 400

    try:
        users = get_users_collection()
        user = users.find_one({"email": email})
    except (ServerSelectionTimeoutError, PyMongoError) as e:
        return jsonify({"detail": "Database unavailable", "error": str(e)}), 503
    if not user or not check_password_hash(user.get("password_hash", ""), password):
        return jsonify({"detail": "Invalid email or password"}), 401

    token = _create_token(email)
    return jsonify({"access_token": token, "token_type": "bearer"}), 200


def _get_email_from_token() -> str | None:
    auth_header = request.headers.get("Authorization", "")
    token = None
    if auth_header.startswith("Bearer "):
        token = auth_header.split(" ", 1)[1].strip()
    if not token:
        # support query param fallback (frontend passes email for now)
        return None
    try:
        payload = jwt.decode(token, _jwt_secret(), algorithms=["HS256"])
        return payload.get("sub")
    except Exception:
        return None


@bp.route("/auth/me", methods=["GET"])
def me():
    # Prefer JWT; fallback to email query param to match current frontend flow
    email = _get_email_from_token() or (request.args.get("email", "").strip().lower())
    if not email:
        return jsonify({"detail": "Unauthorized"}), 401

    try:
        users = get_users_collection()
        user = users.find_one({"email": email}, {"_id": 0, "password_hash": 0})
    except (ServerSelectionTimeoutError, PyMongoError) as e:
        return jsonify({"detail": "Database unavailable", "error": str(e)}), 503
    if not user:
        # If JWT is valid but user doc missing, still return basic profile
        user = {"email": email}

    return jsonify(user), 200
