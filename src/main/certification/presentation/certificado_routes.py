from io import BytesIO

import qrcode
from flask import Blueprint, jsonify, send_file, session, url_for
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from bootstrap.dependencies import container
from shared.http_messages import NOT_AUTHENTICATED, COMPANY_NOT_FOUND, CERTIFICATE_NOT_FOUND


certificado_bp = Blueprint("certificado", __name__, url_prefix="/certificados")


def build_certificacion_service():
    return container.get_certificacion_service()


def serialize_certificado(certificado):
    return {
        "id": certificado.id,
        "practica_id": certificado.internship_id,
        "codigo_qr": {
            "valor": certificado.codigo_qr.value,
            "url_verificacion": (
                certificado.codigo_qr.url_verificacion
                or f"/certificados/verificar/{certificado.codigo_qr.value}"
            ),
            "imagen_url": f"/certificados/{certificado.codigo_qr.value}/qr",
        } if certificado.codigo_qr else None,
        "documento": {
            "url": (
                certificado.documento.url
                or f"/certificados/practica/{certificado.internship_id}/pdf"
            ),
        } if certificado.documento else None,
    }


def get_authenticated_user_id():
    return session.get("usuario_id")


@certificado_bp.post("/<int:internship_id>/emitir")
def issue_certificado(internship_id):
    user_id = get_authenticated_user_id()
    if user_id is None:
        return jsonify({"error": NOT_AUTHENTICATED}), 401

    profile_repository = container.get_profile_repository()
    company = profile_repository.find_company_by_user_id(user_id)
    if company is None:
        return jsonify({"error": COMPANY_NOT_FOUND}), 403

    certificado, creado = build_certificacion_service().issue_certificate(
        company.id, internship_id
    )

    return jsonify(serialize_certificado(certificado)), 201 if creado else 200


@certificado_bp.get("/verificar/<codigo_qr_valor>")
def verify_certificado(codigo_qr_valor):
    is_valid = build_certificacion_service().verify_certificate(codigo_qr_valor)

    return jsonify({"codigo_qr_valor": codigo_qr_valor, "valido": is_valid}), 200


@certificado_bp.get("/practica/<int:internship_id>")
def get_certificado_by_practica(internship_id):
    user_id = get_authenticated_user_id()
    if user_id is None:
        return jsonify({"error": NOT_AUTHENTICATED}), 401

    practica_service = container.get_internship_service()
    practica_service.get_for_user(user_id, internship_id)
    certificado = build_certificacion_service().find_by_practica_id(internship_id)
    if certificado is None:
        return jsonify({"error": CERTIFICATE_NOT_FOUND}), 404
    return jsonify(serialize_certificado(certificado)), 200


@certificado_bp.get("/practica/<int:internship_id>/pdf")
def download_certificado_pdf(internship_id):
    user_id = get_authenticated_user_id()
    if user_id is None:
        return jsonify({"error": NOT_AUTHENTICATED}), 401
    container.get_internship_service().get_for_user(user_id, internship_id)
    certificado = container.get_certificado_repository().find_by_practica_id(internship_id)
    if certificado is None or certificado.documento is None:
        return jsonify({"error": CERTIFICATE_NOT_FOUND}), 404
    if not certificado.verificar_integridad(certificado.documento.contenido):
        return jsonify({"error": "El certificado perdió su integridad"}), 409

    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    ancho, alto = A4
    pdf.setTitle(f"Certificado de práctica {internship_id}")
    pdf.setFont("Helvetica-Bold", 20)
    pdf.drawCentredString(ancho / 2, alto - 120, "CERTIFICADO DE PRÁCTICAS")
    pdf.setFont("Helvetica", 12)
    text = pdf.beginText(72, alto - 190)
    for line in (certificado.documento.contenido or "").splitlines() or [""]:
        text.textLine(line)
    text.textLine("")
    text.textLine(f"Código de verificación: {certificado.codigo_qr.value}")
    pdf.drawText(text)
    pdf.save()
    buffer.seek(0)
    return send_file(
        buffer,
        mimetype="application/pdf",
        as_attachment=True,
        download_name=f"certificado-practica-{internship_id}.pdf",
    )


@certificado_bp.get("/<codigo_qr_valor>/qr")
def download_certificado_qr(codigo_qr_valor):
    certificado = container.get_certificado_repository().find_by_codigo(codigo_qr_valor)
    if certificado is None or certificado.codigo_qr is None:
        return jsonify({"error": CERTIFICATE_NOT_FOUND}), 404

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
