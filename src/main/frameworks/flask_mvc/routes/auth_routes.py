from flask import Blueprint, current_app, jsonify, request, session

from application.email_delivery_error import EmailDeliveryError
from bootstrap.dependencies import container
from shared.http_messages import NO_AUTENTICADO

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


def build_usuario_service():
    return container.get_usuario_service()


def serialize_usuario(usuario):
    return {
        "id": usuario.id,
        "email": usuario.email,
        "tipo": usuario.tipo,
        "estado": usuario.estado,
    }


@auth_bp.post("/register")
def register():
    payload = request.get_json(silent=True) or {}
    try:
        usuario = build_usuario_service().register_user(
            email=payload.get("email"),
            password=payload.get("password"),
            password_confirmation=payload.get("password_confirmation"),
            tipo=payload.get("tipo"),
        )
    except EmailDeliveryError as exc:
        return jsonify({"error": str(exc)}), 503
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    data = serialize_usuario(usuario)
    if current_app.config["EXPOSE_AUTH_TOKENS"]:
        data["activation_token"] = usuario.activation_token
    return jsonify(data), 201


@auth_bp.post("/login")
def login():
    payload = request.get_json(silent=True) or {}
    try:
        usuario = build_usuario_service().authenticate(
            email=payload.get("email"),
            password=payload.get("password"),
        )
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 401

    session.clear()
    session["usuario_id"] = usuario.id
    return jsonify(serialize_usuario(usuario)), 200


@auth_bp.post("/activate")
def activate():
    payload = request.get_json(silent=True) or {}
    try:
        usuario = build_usuario_service().activate_account(token=payload.get("token"))
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify(serialize_usuario(usuario)), 200


@auth_bp.post("/recover-password")
def recover_password():
    payload = request.get_json(silent=True) or {}
    try:
        usuario = build_usuario_service().recover_password(email=payload.get("email"))
    except EmailDeliveryError as exc:
        return jsonify({"error": str(exc)}), 503
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    data = {"status": "ok"}
    if usuario is not None and current_app.config["EXPOSE_AUTH_TOKENS"]:
        data["password_reset_token"] = usuario.password_reset_token
    return jsonify(data), 200


@auth_bp.post("/resend-activation")
def resend_activation():
    payload = request.get_json(silent=True) or {}
    try:
        usuario = build_usuario_service().resend_activation(email=payload.get("email"))
    except EmailDeliveryError as exc:
        return jsonify({"error": str(exc)}), 503
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    data = {
        "status": "ok",
        "message": (
            "Si la cuenta existe y está pendiente, recibirás un nuevo "
            "enlace de activación."
        ),
    }
    if usuario is not None and current_app.config["EXPOSE_AUTH_TOKENS"]:
        data["activation_token"] = usuario.activation_token
    return jsonify(data), 200


@auth_bp.post("/reset-password")
def reset_password():
    payload = request.get_json(silent=True) or {}
    try:
        usuario = build_usuario_service().reset_password(
            token=payload.get("token"),
            new_password=payload.get("new_password"),
        )
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify(serialize_usuario(usuario)), 200


@auth_bp.post("/logout")
def logout():
    session.pop("usuario_id", None)
    return jsonify({"status": "ok"})


@auth_bp.get("/me")
def me():
    usuario_id = session.get("usuario_id")
    if usuario_id is None:
        return jsonify({"error": NO_AUTENTICADO}), 401

    usuario = build_usuario_service().find_by_id(usuario_id)
    if usuario is None:
        session.pop("usuario_id", None)
        return jsonify({"error": "Usuario no encontrado"}), 404

    return jsonify(serialize_usuario(usuario)), 200
