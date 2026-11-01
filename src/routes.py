from functools import wraps
from flask import Blueprint, request, jsonify, g
from src.database import SessionLocal
from src.schemas import UserCreate, UserResponse, ApiKeyCreate, ApiKeyResponse, ApiKeyValidate, ApiKeyValidationResponse
from src.service import UserService, ApiKeyService
from sqlalchemy.orm import Session

bp = Blueprint("api", __name__, url_prefix="/api")


def get_db():
    db = SessionLocal()
    try:
        return db
    finally:
        pass


def auth_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth = request.authorization
        if not auth or not auth.username or not auth.password:
            return jsonify({"error": "Authentication required"}), 401

        db = get_db()
        user = UserService.authenticate_user(db, auth.username, auth.password)
        db.close()
        if not user:
            return jsonify({"error": "Invalid credentials"}), 401

        g.current_user = user
        return f(*args, **kwargs)

    return decorated_function


@bp.route("/users/register", methods=["POST"])
def register():
    db = get_db()
    try:
        data = request.get_json()
        user_data = UserCreate(**data)

        existing_user = UserService.get_user_by_username(db, user_data.username)
        if existing_user:
            return jsonify({"error": "Username already exists"}), 400

        user = UserService.create_user(db, user_data)
        return jsonify(UserResponse.model_validate(user).model_dump()), 201
    finally:
        db.close()


@bp.route("/api-keys", methods=["POST"])
@auth_required
def create_api_key():
    db = get_db()
    try:
        data = request.get_json()
        key_data = ApiKeyCreate(**data)

        api_key = ApiKeyService.create_api_key(db, g.current_user.id, key_data)
        return jsonify(ApiKeyResponse.model_validate(api_key).model_dump()), 201
    finally:
        db.close()


@bp.route("/api-keys", methods=["GET"])
@auth_required
def list_api_keys():
    db = get_db()
    try:
        api_keys = ApiKeyService.get_user_api_keys(db, g.current_user.id)
        return jsonify([ApiKeyResponse.model_validate(key).model_dump() for key in api_keys]), 200
    finally:
        db.close()


@bp.route("/api-keys/<int:key_id>/revoke", methods=["POST"])
@auth_required
def revoke_api_key(key_id: int):
    db = get_db()
    try:
        api_key = ApiKeyService.revoke_api_key(db, key_id, g.current_user.id)
        if not api_key:
            return jsonify({"error": "API key not found"}), 404
        return jsonify(ApiKeyResponse.model_validate(api_key).model_dump()), 200
    finally:
        db.close()


@bp.route("/api-keys/validate", methods=["POST"])
def validate_api_key():
    db = get_db()
    try:
        data = request.get_json()
        key_data = ApiKeyValidate(**data)

        validation_result = ApiKeyService.validate_api_key(db, key_data.key_value)
        return jsonify(ApiKeyValidationResponse(**validation_result).model_dump()), 200
    finally:
        db.close()


@bp.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "healthy"}), 200
