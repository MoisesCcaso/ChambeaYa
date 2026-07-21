from flask import Blueprint, jsonify, request, session

from application.convocatoria_application_service import ConvocatoriaApplicationService
from infrastructure.sqlalchemy_convocatoria_repository import SqlAlchemyConvocatoriaRepository
from infrastructure.sqlalchemy_perfil_repository import SqlAlchemyPerfilRepository
from presentation.convocatoria_controller import ConvocatoriaController


convocatoria_bp = Blueprint("convocatoria", __name__, url_prefix="/convocatorias")


def build_convocatoria_controller():
    convocatoria_repository = SqlAlchemyConvocatoriaRepository()
    service = ConvocatoriaApplicationService(convocatoria_repository)
    return ConvocatoriaController(service)


def get_authenticated_user_id():
    return session.get("usuario_id")


@convocatoria_bp.post("")
def create_convocatoria():
    usuario_id = get_authenticated_user_id()
    if usuario_id is None:
        return jsonify({"error": "No autenticado"}), 401

    perfil_repository = SqlAlchemyPerfilRepository()
    empresa = perfil_repository.find_empresa_by_user_id(usuario_id)
    if empresa is None:
        return jsonify({"error": "Empresa no encontrada para este usuario"}), 400

    payload = request.get_json(silent=True) or {}
    controller = build_convocatoria_controller()
    try:
        data, status_code = controller.create(empresa.id, payload)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify(data), status_code

@convocatoria_bp.post("/<int:convocatoria_id>/publicar")
def publish_convocatoria(convocatoria_id):
    usuario_id = get_authenticated_user_id()
    if usuario_id is None:
        return jsonify({"error": "No autenticado"}), 401

    perfil_repository = SqlAlchemyPerfilRepository()
    empresa = perfil_repository.find_empresa_by_user_id(usuario_id)
    if empresa is None:
        return jsonify({"error": "Empresa no encontrada para este usuario"}), 400

    controller = build_convocatoria_controller()
    try:
        data, status_code = controller.publish(empresa.id, convocatoria_id)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify(data), status_code