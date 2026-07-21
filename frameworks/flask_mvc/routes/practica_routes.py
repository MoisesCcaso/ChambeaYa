from flask import Blueprint, jsonify, request, session

from application.practica_application_service import PracticaApplicationService
from infrastructure.sqlalchemy_perfil_repository import SqlAlchemyPerfilRepository
from infrastructure.sqlalchemy_practica_repository import SqlAlchemyPracticaRepository
from presentation.practica_controller import PracticaController


_UNAUTHORIZED = "No autenticado"

practica_bp = Blueprint("practica", __name__, url_prefix="/practicas")


def build_practica_controller():
    practica_repository = SqlAlchemyPracticaRepository()
    perfil_repository = SqlAlchemyPerfilRepository()
    service = PracticaApplicationService(practica_repository, perfil_repository)
    return PracticaController(service)


def get_authenticated_user_id():
    return session.get("usuario_id")


@practica_bp.get("")
def list_practicas():
    usuario_id = get_authenticated_user_id()
    if usuario_id is None:
        return jsonify({"error": _UNAUTHORIZED}), 401

    controller = build_practica_controller()
    try:
        data, status_code = controller.list_mis_practicas(usuario_id)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify(data), status_code


@practica_bp.post("/<int:practica_id>/entregables")
def subir_entregable(practica_id):
    usuario_id = get_authenticated_user_id()
    if usuario_id is None:
        return jsonify({"error": _UNAUTHORIZED}), 401

    payload = request.get_json(silent=True) or {}
    controller = build_practica_controller()
    try:
        data, status_code = controller.subir_entregable(usuario_id, practica_id, payload)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify(data), status_code
