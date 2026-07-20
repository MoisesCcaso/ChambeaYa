from flask import Blueprint, jsonify, request, session

from application.practica_application_service import PracticaApplicationService
from infrastructure.sqlalchemy_practica_repository import SqlAlchemyPracticaRepository
from infrastructure.sqlalchemy_perfil_repository import SqlAlchemyPerfilRepository
from presentation.practica_controller import PracticaController


practica_bp = Blueprint("practica", __name__, url_prefix="/practica")


def build_practica_controller():
    practica_repository = SqlAlchemyPracticaRepository()
    perfil_repository = SqlAlchemyPerfilRepository()
    service = PracticaApplicationService(practica_repository, perfil_repository)
    return PracticaController(service)


def get_authenticated_user_id():
    return session.get("usuario_id")


@practica_bp.post("/<int:practica_id>/entregables")
def upload_deliverable(practica_id):
    usuario_id = get_authenticated_user_id()
    if usuario_id is None:
        return jsonify({"error": "No autenticado"}), 401

    payload = request.get_json(silent=True) or {}
    controller = build_practica_controller()
    try:
        data, status_code = controller.upload_deliverable(usuario_id, practica_id, payload)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify(data), status_code


@practica_bp.get("/<int:practica_id>/entregables")
def get_deliverables_history(practica_id):
    usuario_id = get_authenticated_user_id()
    if usuario_id is None:
        return jsonify({"error": "No autenticado"}), 401

    controller = build_practica_controller()
    try:
        data, status_code = controller.get_deliverables_history(usuario_id, practica_id)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify(data), status_code


@practica_bp.get("/<int:practica_id>/evaluaciones")
def get_evaluations_history(practica_id):
    usuario_id = get_authenticated_user_id()
    if usuario_id is None:
        return jsonify({"error": "No autenticado"}), 401

    controller = build_practica_controller()
    try:
        data, status_code = controller.get_evaluations_history(usuario_id, practica_id)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify(data), status_code