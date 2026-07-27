from io import BytesIO

import qrcode
from flask import Blueprint, current_app, jsonify, send_file, session, url_for
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from application.certificacion_application_service import CertificacionApplicationService
from application.notificacion_application_service import NotificacionApplicationService
from application.practica_application_service import PracticaApplicationService
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
            current_app.logger.exception(
                "No se pudo crear la notificación de certificado emitido"
            )

    return jsonify(data), status_code


@certificado_bp.get("/verificar/<codigo_qr_valor>")
def verify_certificado(codigo_qr_valor):
    controller = build_certificado_controller()
    try:
        data, status_code = controller.verify(codigo_qr_valor)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify(data), status_code


@certificado_bp.get("/practica/<int:practica_id>")
def get_certificado_by_practica(practica_id):
    usuario_id = get_authenticated_user_id()
    if usuario_id is None:
        return jsonify({"error": NO_AUTENTICADO_ERROR}), 401

    practica_service = PracticaApplicationService(
        SqlAlchemyPracticaRepository(),
        SqlAlchemyPerfilRepository(),
        SqlAlchemyPostulacionRepository(),
        SqlAlchemyConvocatoriaRepository(),
    )
    try:
        practica_service.get_for_user(usuario_id, practica_id)
        data, status_code = build_certificado_controller().get_by_practica(practica_id)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 404
    return jsonify(data), status_code


@certificado_bp.get("/practica/<int:practica_id>/pdf")
def download_certificado_pdf(practica_id):
    certificado = SqlAlchemyCertificadoRepository().find_by_practica_id(practica_id)
    if certificado is None or certificado.documento is None:
        return jsonify({"error": "Certificado no encontrado"}), 404
    if not certificado.verificar_integridad(certificado.documento.contenido):
        return jsonify({"error": "El certificado perdió su integridad"}), 409

    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    ancho, alto = A4
    pdf.setTitle(f"Certificado de práctica {practica_id}")
    pdf.setFont("Helvetica-Bold", 20)
    pdf.drawCentredString(ancho / 2, alto - 120, "CERTIFICADO DE PRÁCTICAS")
    pdf.setFont("Helvetica", 12)
    text = pdf.beginText(72, alto - 190)
    for line in (certificado.documento.contenido or "").splitlines() or [""]:
        text.textLine(line)
    text.textLine("")
    text.textLine(f"Código de verificación: {certificado.codigo_qr.valor}")
    pdf.drawText(text)
    pdf.save()
    buffer.seek(0)
    return send_file(
        buffer,
        mimetype="application/pdf",
        as_attachment=True,
        download_name=f"certificado-practica-{practica_id}.pdf",
    )


@certificado_bp.get("/<codigo_qr_valor>/qr")
def download_certificado_qr(codigo_qr_valor):
    certificado = SqlAlchemyCertificadoRepository().find_by_codigo(codigo_qr_valor)
    if certificado is None or certificado.codigo_qr is None:
        return jsonify({"error": "Certificado no encontrado"}), 404

    buffer = BytesIO()
    verification_url = url_for(
        "certificado.verify_certificado",
        codigo_qr_valor=codigo_qr_valor,
        _external=True,
    )
    imagen = qrcode.make(verification_url)
    imagen.save(buffer, format="PNG")
    buffer.seek(0)
    return send_file(buffer, mimetype="image/png")
