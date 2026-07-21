from flask import Blueprint, jsonify, session

from application.convocatoria_application_service import ConvocatoriaApplicationService
from infrastructure.sqlalchemy_convocatoria_repository import SqlAlchemyConvocatoriaRepository
from presentation.convocatoria_controller import ConvocatoriaController


_UNAUTHORIZED = "No autenticado"

convocatoria_bp = Blueprint("convocatoria", __name__, url_prefix="/convocatorias")


def build_convocatoria_controller():
    convocatoria_repository = SqlAlchemyConvocatoriaRepository()
    service = ConvocatoriaApplicationService(convocatoria_repository)
    return ConvocatoriaController(service)


def get_authenticated_user_id():
    return session.get("usuario_id")


@convocatoria_bp.get("")
def list_convocatorias():
    usuario_id = get_authenticated_user_id()
    if usuario_id is None:
        return jsonify({"error": _UNAUTHORIZED}), 401

    controller = build_convocatoria_controller()
    try:
        data, status_code = controller.list_abiertas()
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify(data), status_code
