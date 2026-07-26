from flask import Blueprint, jsonify, session

from application.certificacion_application_service import CertificacionApplicationService
from application.notificacion_application_service import NotificacionApplicationService
from infrastructure.sqlalchemy_certificado_repository import SqlAlchemyCertificadoRepository
from infrastructure.sqlalchemy_notificacion_repository import SqlAlchemyNotificacionRepository
from infrastructure.sqlalchemy_practica_repository import SqlAlchemyPracticaRepository
from infrastructure.sqlalchemy_postulacion_repository import SqlAlchemyPostulacionRepository
from infrastructure.sqlalchemy_convocatoria_repository import SqlAlchemyConvocatoriaRepository
from infrastructure.sqlalchemy_perfil_repository import SqlAlchemyPerfilRepository
from presentation.certificado_controller import CertificadoController


certificado_bp = Blueprint("certificado", __name__, url_prefix="/certificados")
NO_AUTENTICADO_ERROR = "No autenticado"


def build_certificado_controller():
    certificado_repository = SqlAlchemyCertificadoRepository()
    practica_repository = SqlAlchemyPracticaRepository()
    postulacion_repository = SqlAlchemyPostulacionRepository()
    convocatoria_repository = SqlAlchemyConvocatoriaRepository()
    perfil_repository = SqlAlchemyPerfilRepository()
    service = CertificacionApplicationService(
        certificado_repository, practica_repository,
        postulacion_repository, convocatoria_repository, perfil_repository
    )
    return CertificadoController(service)


def get_authenticated_user_id():
    return session.get("usuario_id")


@certificado_bp.post("/<int:practica_id>/emitir")
def issue_certificado(practica_id):
    usuario_id = get_authenticated_user_id()
    if usuario_id is None:
        return jsonify({"error": NO_AUTENTICADO_ERROR}), 401

    perfil_repository = SqlAlchemyPerfilRepository()
    empresa = perfil_repository.find_empresa_by_user_id(usuario_id)
    if empresa is None:
        return jsonify({"error": "Empresa no encontrada para este usuario"}), 400

    controller = build_certificado_controller()
    try:
        data, status_code = controller.issue(empresa.id, practica_id)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    if status_code == 201:
        try:
            practica_repo = SqlAlchemyPracticaRepository()
            practica = practica_repo.find_by_id(practica_id)
            if practica and practica.practicante_id:
                perfil_repo = SqlAlchemyPerfilRepository()
                practicante = perfil_repo.find_practicante_by_id(practica.practicante_id)
                if practicante:
                    repo = SqlAlchemyNotificacionRepository()
                    notif_service = NotificacionApplicationService(writer=repo, reader=repo)
                    notif_service.create_notification(
                        usuario_destino_id=practicante.usuario_id,
                        tipo="CERTIFICADO_EMITIDO",
                        mensaje="Tu certificado digital ha sido emitido",
                        metadata={"practica_id": practica_id},
                    )
        except Exception:
            pass

    return jsonify(data), status_code


@certificado_bp.get("/verificar/<codigo_qr_valor>")
def verify_certificado(codigo_qr_valor):
    controller = build_certificado_controller()
    try:
        data, status_code = controller.verify(codigo_qr_valor)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify(data), status_code