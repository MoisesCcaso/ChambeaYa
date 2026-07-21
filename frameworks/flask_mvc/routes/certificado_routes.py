from flask import Blueprint, jsonify, session

from application.certificacion_application_service import CertificacionApplicationService
from infrastructure.sqlalchemy_certificado_repository import SqlAlchemyCertificadoRepository
from infrastructure.sqlalchemy_perfil_repository import SqlAlchemyPerfilRepository
from presentation.certificado_controller import CertificadoController


_UNAUTHORIZED = "No autenticado"

certificado_bp = Blueprint("certificado", __name__, url_prefix="/certificados")


def build_certificado_controller():
    certificado_repository = SqlAlchemyCertificadoRepository()
    perfil_repository = SqlAlchemyPerfilRepository()
    service = CertificacionApplicationService(certificado_repository, perfil_repository)
    return CertificadoController(service)


def get_authenticated_user_id():
    return session.get("usuario_id")


@certificado_bp.get("")
def list_certificados():
    usuario_id = get_authenticated_user_id()
    if usuario_id is None:
        return jsonify({"error": _UNAUTHORIZED}), 401

    controller = build_certificado_controller()
    try:
        data, status_code = controller.list_mis_certificados(usuario_id)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify(data), status_code
