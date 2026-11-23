from io import BytesIO

import qrcode
from flask import Blueprint, current_app, jsonify, send_file, session, url_for
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from frameworks.flask_mvc.dependencies import container


certificado_bp = Blueprint("certificado", __name__, url_prefix="/certificados")
NO_AUTENTICADO_ERROR = "No autenticado"


def build_certificacion_service():
    return container.get_certificacion_service()


def serialize_certificado(certificado):
    return {
        "id": certificado.id,
        "practica_id": certificado.practica_id,
        "codigo_qr": {
            "valor": certificado.codigo_qr.valor,
            "url_verificacion": (
                certificado.codigo_qr.url_verificacion
                or f"/certificados/verificar/{certificado.codigo_qr.valor}"
            ),
            "imagen_url": f"/certificados/{certificado.codigo_qr.valor}/qr",
        } if certificado.codigo_qr else None,
        "documento": {
            "url": (
                certificado.documento.url
                or f"/certificados/practica/{certificado.practica_id}/pdf"
            ),
        } if certificado.documento else None,
    }


def get_authenticated_user_id():
    return session.get("usuario_id")


@certificado_bp.post("/<int:practica_id>/emitir")
def issue_certificado(practica_id):
    usuario_id = get_authenticated_user_id()
    if usuario_id is None:
        return jsonify({"error": NO_AUTENTICADO_ERROR}), 401

    perfil_repository = container.get_perfil_repository()
    empresa = perfil_repository.find_empresa_by_user_id(usuario_id)
    if empresa is None:
        return jsonify({"error": "Empresa no encontrada para este usuario"}), 400

    try:
        certificado, creado = build_certificacion_service().issue_certificate(
            empresa.id, practica_id
        )
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify(serialize_certificado(certificado)), 201 if creado else 200


@certificado_bp.get("/verificar/<codigo_qr_valor>")
def verify_certificado(codigo_qr_valor):
    try:
        es_valido = build_certificacion_service().verify_certificate(codigo_qr_valor)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify({"codigo_qr_valor": codigo_qr_valor, "valido": es_valido}), 200


@certificado_bp.get("/practica/<int:practica_id>")
def get_certificado_by_practica(practica_id):
    usuario_id = get_authenticated_user_id()
    if usuario_id is None:
        return jsonify({"error": NO_AUTENTICADO_ERROR}), 401

    practica_service = container.get_practica_service()
    try:
        practica_service.get_for_user(usuario_id, practica_id)
        certificado = build_certificacion_service().find_by_practica_id(practica_id)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 404
    if certificado is None:
        return jsonify({"error": "Certificado no encontrado"}), 404
    return jsonify(serialize_certificado(certificado)), 200


@certificado_bp.get("/practica/<int:practica_id>/pdf")
def download_certificado_pdf(practica_id):
    certificado = container.get_certificado_repository().find_by_practica_id(practica_id)
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
    certificado = container.get_certificado_repository().find_by_codigo(codigo_qr_valor)
    if certificado is None or certificado.codigo_qr is None:
        return jsonify({"error": "Certificado no encontrado"}), 404

    buffer = BytesIO()
    verification_url = url_for(
        "web.verify_certificate_view",
        codigo=codigo_qr_valor,
        _external=True,
    )
    imagen = qrcode.make(verification_url)
    imagen.save(buffer, format="PNG")
    buffer.seek(0)
    return send_file(buffer, mimetype="image/png")
