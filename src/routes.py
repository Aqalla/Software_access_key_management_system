from functools import wraps
from datetime import datetime
from flask import Blueprint, request, jsonify, g, render_template, session, redirect, url_for, flash
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


# Web routes for frontend
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('user_id'):
            return redirect('/api/login')
        return f(*args, **kwargs)
    return decorated_function


@bp.route("/register", methods=["GET"], endpoint="register_page")
def register_page():
    return render_template("register.html")


@bp.route("/register", methods=["POST"], endpoint="register_submit")
def register():
    db = get_db()
    try:
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            flash('Заполните все поля', 'error')
            return redirect('/api/register')

        user_data = UserCreate(username=username, password=password)
        existing_user = UserService.get_user_by_username(db, user_data.username)
        if existing_user:
            flash('Пользователь с таким именем уже существует', 'error')
            return redirect('/api/register')

        user = UserService.create_user(db, user_data)
        flash('Регистрация успешна! Теперь войдите в систему.', 'success')
        return redirect('/api/login')
    finally:
        db.close()


@bp.route("/login", methods=["GET"], endpoint="login_page")
def login_page():
    return render_template("login.html")


@bp.route("/login", methods=["POST"], endpoint="login_submit")
def login():
    db = get_db()
    try:
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            flash('Заполните все поля', 'error')
            return redirect('/api/login')

        user = UserService.authenticate_user(db, username, password)
        if not user:
            flash('Неверное имя пользователя или пароль', 'error')
            return redirect('/api/login')

        session['user_id'] = user.id
        session['username'] = user.username
        flash('Добро пожаловать!', 'success')
        return redirect('/api/dashboard')
    finally:
        db.close()


@bp.route("/logout", methods=["GET"])
def logout():
    session.clear()
    flash('Вы вышли из системы', 'info')
    return redirect('/api/login')


@bp.route("/dashboard", methods=["GET"])
@login_required
def dashboard():
    db = get_db()
    try:
        user_id = session.get('user_id')
        api_keys = ApiKeyService.get_user_api_keys(db, user_id)
        return render_template("dashboard.html", keys=api_keys, now=datetime.utcnow())
    finally:
        db.close()


@bp.route("/create-key", methods=["GET"], endpoint="create_key_page")
@login_required
def create_key_page():
    return render_template("create_key.html")


@bp.route("/create-key", methods=["POST"], endpoint="create_key_submit")
@login_required
def create_key():
    db = get_db()
    try:
        user_id = session.get('user_id')
        name = request.form.get('name')
        description = request.form.get('description')
        expires_at = request.form.get('expires_at')

        if not name:
            flash('Введите название ключа', 'error')
            return redirect('/api/create-key')

        key_data = ApiKeyCreate(
            name=name,
            description=description if description else None,
            expires_in_days=None,
            expires_at=expires_at if expires_at else None
        )

        api_key = ApiKeyService.create_api_key(db, user_id, key_data)
        flash('API ключ успешно создан!', 'success')
        return render_template("create_key.html", new_key=api_key)
    finally:
        db.close()


@bp.route("/keys/<int:key_id>/revoke", methods=["POST"])
@login_required
def revoke_key_page(key_id: int):
    db = get_db()
    try:
        user_id = session.get('user_id')
        api_key = ApiKeyService.revoke_api_key(db, key_id, user_id)
        if not api_key:
            flash('API ключ не найден', 'error')
        else:
            flash('API ключ успешно отозван', 'success')
        return redirect('/api/dashboard')
    finally:
        db.close()


@bp.route("/validate", methods=["GET"], endpoint="validate_page")
def validate_page():
    return render_template("validate.html")


@bp.route("/validate", methods=["POST"], endpoint="validate_submit")
def validate_key():
    db = get_db()
    try:
        key_value = request.form.get('key_value')
        if not key_value:
            flash('Введите API ключ', 'error')
            return redirect('/api/validate')

        validation_result = ApiKeyService.validate_api_key(db, key_value)
        return render_template("validate.html", validation_result=validation_result)
    finally:
        db.close()


@bp.route("/", methods=["GET"])
def index():
    if session.get('user_id'):
        return redirect('/api/dashboard')
    return redirect('/api/login')
