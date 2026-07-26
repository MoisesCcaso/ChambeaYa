from flask import Blueprint, jsonify, session

from application.postulacion_application_service import PostulacionApplicationService
from infrastructure.sqlalchemy_postulacion_repository import SqlAlchemyPostulacionRepository
from infrastructure.sqlalchemy_convocatoria_repository import SqlAlchemyConvocatoriaRepository
from infrastructure.sqlalchemy_perfil_repository import SqlAlchemyPerfilRepository
from presentation.postulacion_controller import PostulacionController


postulacion_bp = Blueprint("postulacion", __name__, url_prefix="/postulaciones")


def build_postulacion_controller():
    postulacion_repository = SqlAlchemyPostulacionRepository()
    convocatoria_repository = SqlAlchemyConvocatoriaRepository()
    service = PostulacionApplicationService(postulacion_repository, convocatoria_repository)
    return PostulacionController(service)


def get_authenticated_user_id():
    return session.get("usuario_id")


@postulacion_bp.post("/<int:postulacion_id>/seleccionar")
def select_postulacion(postulacion_id):
    usuario_id = get_authenticated_user_id()
    if usuario_id is None:
        return jsonify({"error": "No autenticado"}), 401

    perfil_repository = SqlAlchemyPerfilRepository()
    empresa = perfil_repository.find_empresa_by_user_id(usuario_id)
    if empresa is None:
        return jsonify({"error": "Empresa no encontrada para este usuario"}), 400

    controller = build_postulacion_controller()
    try:
        data, status_code = controller.select(empresa.id, postulacion_id)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify(data), status_code