from flask import Blueprint, jsonify

from application.certificacion_application_service import CertificacionApplicationService
from frameworks.flask_mvc.routes._helpers import login_required
from infrastructure.sqlalchemy_certificado_repository import SqlAlchemyCertificadoRepository
from infrastructure.sqlalchemy_perfil_repository import SqlAlchemyPerfilRepository
from presentation.certificado_controller import CertificadoController


certificado_bp = Blueprint("certificado", __name__, url_prefix="/certificados")


def build_certificado_controller():
    certificado_repository = SqlAlchemyCertificadoRepository()
    perfil_repository = SqlAlchemyPerfilRepository()
    service = CertificacionApplicationService(certificado_repository, perfil_repository)
    return CertificadoController(service)


@certificado_bp.get("")
@login_required
def list_certificados(usuario_id):
    controller = build_certificado_controller()
    try:
        data, status_code = controller.list_mis_certificados(usuario_id)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify(data), status_code
