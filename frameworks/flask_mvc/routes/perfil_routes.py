from flask import Blueprint, jsonify, request

from application.perfil_application_service import PerfilApplicationService
from frameworks.flask_mvc.routes._helpers import login_required
from infrastructure.sqlalchemy_perfil_repository import SqlAlchemyPerfilRepository
from infrastructure.sqlalchemy_usuario_repository import SqlAlchemyUsuarioRepository
from presentation.perfil_controller import PerfilController


perfil_bp = Blueprint("perfil", __name__, url_prefix="/perfil")


def build_perfil_controller():
    perfil_repository = SqlAlchemyPerfilRepository()
    usuario_repository = SqlAlchemyUsuarioRepository()
    service = PerfilApplicationService(perfil_repository, usuario_repository)
    return PerfilController(service)


@perfil_bp.get("/me")
@login_required
def get_my_profile(usuario_id):
    controller = build_perfil_controller()
    try:
        data, status_code = controller.get_practicante(usuario_id)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    if data is None:
        return jsonify({"error": "Perfil de practicante no encontrado"}), status_code

    return jsonify(data), status_code


@perfil_bp.put("/me")
@login_required
def update_my_profile(usuario_id):
    payload = request.get_json(silent=True) or {}
    controller = build_perfil_controller()
    try:
        data, status_code = controller.update_practicante(usuario_id, payload)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify(data), status_code


@perfil_bp.post("/me/habilidades")
@login_required
def add_my_skill(usuario_id):
    payload = request.get_json(silent=True) or {}
    controller = build_perfil_controller()
    try:
        data, status_code = controller.add_habilidad(usuario_id, payload)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify(data), status_code


@perfil_bp.post("/me/formacion")
@login_required
def add_my_education(usuario_id):
    payload = request.get_json(silent=True) or {}
    controller = build_perfil_controller()
    try:
        data, status_code = controller.add_formacion(usuario_id, payload)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify(data), status_code


@perfil_bp.post("/me/identidad")
@login_required
def verify_my_identity(usuario_id):
    payload = request.get_json(silent=True) or {}
    controller = build_perfil_controller()
    try:
        data, status_code = controller.verify_identity(usuario_id, payload)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify(data), status_code


@perfil_bp.get("/me/reputacion")
@login_required
def get_my_reputation(usuario_id):
    controller = build_perfil_controller()
    try:
        data, status_code = controller.get_reputation_score(usuario_id)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify(data), status_code


@perfil_bp.get("/me/reporte-reputacion")
@login_required
def get_my_reputation_report(usuario_id):
    controller = build_perfil_controller()
    try:
        data, status_code = controller.get_reputation_report(usuario_id)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify(data), status_code
