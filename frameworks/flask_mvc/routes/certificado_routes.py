from flask import Blueprint, jsonify, request, session

from application.certificacion_application_service import CertificacionApplicationService
from domain.certificacion.certificacion_dominio_servicio import CertificacionDominioServicio
from infrastructure.sqlalchemy_certificado_repository import SqlAlchemyCertificadoRepository
from infrastructure.sqlalchemy_perfil_repository import SqlAlchemyPerfilRepository
from infrastructure.sqlalchemy_practica_repository import SqlAlchemyPracticaRepository
from presentation.certificado_controller import CertificadoController


certificado_bp = Blueprint("certificado", __name__, url_prefix="/certificados")


def build_certificado_controller():
    cert_repo = SqlAlchemyCertificadoRepository()
    prac_repo = SqlAlchemyPracticaRepository()
    per_repo = SqlAlchemyPerfilRepository()
    servicio = CertificacionDominioServicio()
    app_service = CertificacionApplicationService(cert_repo, prac_repo, per_repo, servicio)
    return CertificadoController(app_service)


@certificado_bp.post("/emitir")
def issue_certificate():
    usuario_id = session.get("usuario_id")

    if usuario_id is None:
        return jsonify({"error": "No autenticado"}), 401

    payload = request.get_json(silent=True) or {}
    controller = build_certificado_controller()

    try:
        data, status_code = controller.issue(payload)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify(data), status_code


@certificado_bp.get("/verificar/<codigo>")
def verify_certificate(codigo):
    controller = build_certificado_controller()

    try:
        data, status_code = controller.verify(codigo)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify(data), status_code
