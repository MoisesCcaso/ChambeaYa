from flask import Blueprint, jsonify, request, session

from application.usuario_application_service import UsuarioApplicationService
from infrastructure.sqlalchemy_usuario_repository import SqlAlchemyUsuarioRepository
from presentation.usuario_controller import UsuarioController


auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


def build_usuario_controller():
    repository = SqlAlchemyUsuarioRepository()
    service = UsuarioApplicationService(repository)
    return UsuarioController(service)


@auth_bp.post("/register")
def register():
    payload = request.get_json(silent=True) or {}
    controller = build_usuario_controller()

    try:
        data, status_code = controller.register(payload)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify(data), status_code


@auth_bp.post("/login")
def login():
    payload = request.get_json(silent=True) or {}
    controller = build_usuario_controller()

    try:
        data, status_code = controller.login(payload)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 401

    session["usuario_id"] = data["id"]
    return jsonify(data), status_code


@auth_bp.post("/activate")
def activate():
    payload = request.get_json(silent=True) or {}
    controller = build_usuario_controller()

    try:
        data, status_code = controller.activate_account(payload)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify(data), status_code


@auth_bp.post("/recover-password")
def recover_password():
    payload = request.get_json(silent=True) or {}
    controller = build_usuario_controller()

    try:
        data, status_code = controller.recover_password(payload)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify(data), status_code


@auth_bp.post("/reset-password")
def reset_password():
    payload = request.get_json(silent=True) or {}
    controller = build_usuario_controller()

    try:
        data, status_code = controller.reset_password(payload)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify(data), status_code


@auth_bp.post("/logout")
def logout():
    session.pop("usuario_id", None)
    return jsonify({"status": "ok"})


@auth_bp.get("/me")
def me():
    usuario_id = session.get("usuario_id")
    if usuario_id is None:
        return jsonify({"error": "No autenticado"}), 401

    controller = build_usuario_controller()
    try:
        data, status_code = controller.get_authenticated_user(usuario_id)
    except ValueError as exc:
        session.pop("usuario_id", None)
        return jsonify({"error": str(exc)}), 404

    return jsonify(data), status_code
