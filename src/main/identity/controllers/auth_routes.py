from flask import Blueprint, current_app, jsonify, request, session
from flask_wtf.csrf import generate_csrf

from bootstrap.dependencies import container
from shared.http_messages import NOT_AUTHENTICATED

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


def build_user_service():
    return container.get_user_service()


def serialize_user(user):
    return {
        "id": user.id,
        "email": user.email,
        "tipo": user.role,
        "estado": user.status,
    }


@auth_bp.get("/csrf-token")
def csrf_token():
    """Gives API clients the token to send in the X-CSRFToken header."""
    return jsonify({"csrf_token": generate_csrf()}), 200


@auth_bp.post("/register")
def register():
    payload = request.get_json(silent=True) or {}
    user = build_user_service().register_user(
        email=payload.get("email"),
        password=payload.get("password"),
        password_confirmation=payload.get("password_confirmation"),
        role=payload.get("tipo"),
    )

    data = serialize_user(user)
    if current_app.config["EXPOSE_AUTH_TOKENS"]:
        data["activation_token"] = user.activation_token
    return jsonify(data), 201


@auth_bp.post("/login")
def login():
    payload = request.get_json(silent=True) or {}
    user = build_user_service().authenticate(
        email=payload.get("email"),
        password=payload.get("password"),
    )

    session.clear()
    session["usuario_id"] = user.id
    return jsonify(serialize_user(user)), 200


@auth_bp.post("/activate")
def activate():
    payload = request.get_json(silent=True) or {}
    user = build_user_service().activate_account(token=payload.get("token"))

    return jsonify(serialize_user(user)), 200


@auth_bp.post("/recover-password")
def recover_password():
    payload = request.get_json(silent=True) or {}
    user = build_user_service().recover_password(email=payload.get("email"))

    data = {"status": "ok"}
    if user is not None and current_app.config["EXPOSE_AUTH_TOKENS"]:
        data["password_reset_token"] = user.password_reset_token
    return jsonify(data), 200


@auth_bp.post("/resend-activation")
def resend_activation():
    payload = request.get_json(silent=True) or {}
    user = build_user_service().resend_activation(email=payload.get("email"))

    data = {
        "status": "ok",
        "message": (
            "Si la cuenta existe y está pendiente, recibirás un nuevo "
            "enlace de activación."
        ),
    }
    if user is not None and current_app.config["EXPOSE_AUTH_TOKENS"]:
        data["activation_token"] = user.activation_token
    return jsonify(data), 200


@auth_bp.post("/reset-password")
def reset_password():
    payload = request.get_json(silent=True) or {}
    user = build_user_service().reset_password(
        token=payload.get("token"),
        new_password=payload.get("new_password"),
    )

    return jsonify(serialize_user(user)), 200


@auth_bp.post("/logout")
def logout():
    session.pop("usuario_id", None)
    return jsonify({"status": "ok"})


@auth_bp.get("/me")
def me():
    user_id = session.get("usuario_id")
    if user_id is None:
        return jsonify({"error": NOT_AUTHENTICATED}), 401

    user = build_user_service().find_by_id(user_id)
    if user is None:
        session.pop("usuario_id", None)
        return jsonify({"error": "Usuario no encontrado"}), 404

    return jsonify(serialize_user(user)), 200
