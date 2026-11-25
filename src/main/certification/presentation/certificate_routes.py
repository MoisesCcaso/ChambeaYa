from io import BytesIO

import qrcode
from flask import Blueprint, jsonify, send_file, session, url_for
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from bootstrap.dependencies import container
from shared.http_messages import NOT_AUTHENTICATED, COMPANY_NOT_FOUND, CERTIFICATE_NOT_FOUND


certificate_bp = Blueprint("certificado", __name__, url_prefix="/certificados")


def build_certification_service():
    return container.get_certification_service()


def serialize_certificate(certificate):
    return {
        "id": certificate.id,
        "practica_id": certificate.internship_id,
        "codigo_qr": {
            "valor": certificate.qr_code.value,
            "url_verificacion": (
                certificate.qr_code.verification_url
                or f"/certificados/verificar/{certificate.qr_code.value}"
            ),
            "imagen_url": f"/certificados/{certificate.qr_code.value}/qr",
        } if certificate.qr_code else None,
        "documento": {
            "url": (
                certificate.document.url
                or f"/certificados/practica/{certificate.internship_id}/pdf"
            ),
        } if certificate.document else None,
    }


def get_authenticated_user_id():
    return session.get("usuario_id")


@certificate_bp.post("/<int:internship_id>/emitir")
def issue_certificate_route(internship_id):
    user_id = get_authenticated_user_id()
    if user_id is None:
        return jsonify({"error": NOT_AUTHENTICATED}), 401

    profile_repository = container.get_profile_repository()
    company = profile_repository.find_company_by_user_id(user_id)
    if company is None:
        return jsonify({"error": COMPANY_NOT_FOUND}), 403

    certificate, created = build_certification_service().issue_certificate(
        company.id, internship_id
    )

    return jsonify(serialize_certificate(certificate)), 201 if created else 200


@certificate_bp.get("/verificar/<qr_code_value>")
def verify_certificate_route(qr_code_value):
    is_valid = build_certification_service().verify_certificate(qr_code_value)

    return jsonify({"codigo_qr_valor": qr_code_value, "valido": is_valid}), 200


@certificate_bp.get("/practica/<int:internship_id>")
def get_certificate_by_internship(internship_id):
    user_id = get_authenticated_user_id()
    if user_id is None:
        return jsonify({"error": NOT_AUTHENTICATED}), 401

    internship_service = container.get_internship_service()
    internship_service.get_for_user(user_id, internship_id)
    certificate = build_certification_service().find_by_internship_id(internship_id)
    if certificate is None:
        return jsonify({"error": CERTIFICATE_NOT_FOUND}), 404
    return jsonify(serialize_certificate(certificate)), 200


@certificate_bp.get("/practica/<int:internship_id>/pdf")
def download_certificate_pdf(internship_id):
    user_id = get_authenticated_user_id()
    if user_id is None:
        return jsonify({"error": NOT_AUTHENTICATED}), 401
    container.get_internship_service().get_for_user(user_id, internship_id)
    certificate = container.get_certificate_repository().find_by_internship_id(internship_id)
    if certificate is None or certificate.document is None:
        return jsonify({"error": CERTIFICATE_NOT_FOUND}), 404
    if not certificate.verify_integrity(certificate.document.content):
        return jsonify({"error": "El certificado perdió su integridad"}), 409

    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    pdf.setTitle(f"Certificado de práctica {internship_id}")
    pdf.setFont("Helvetica-Bold", 20)
    pdf.drawCentredString(width / 2, height - 120, "CERTIFICADO DE PRÁCTICAS")
    pdf.setFont("Helvetica", 12)
    text = pdf.beginText(72, height - 190)
    for line in (certificate.document.content or "").splitlines() or [""]:
        text.textLine(line)
    text.textLine("")
    text.textLine(f"Código de verificación: {certificate.qr_code.value}")
    pdf.drawText(text)
    pdf.save()
    buffer.seek(0)
    return send_file(
        buffer,
        mimetype="application/pdf",
        as_attachment=True,
        download_name=f"certificado-practica-{internship_id}.pdf",
    )


@certificate_bp.get("/<qr_code_value>/qr")
def download_certificate_qr(qr_code_value):
    certificate = container.get_certificate_repository().find_by_code(qr_code_value)
    if certificate is None or certificate.qr_code is None:
        return jsonify({"error": CERTIFICATE_NOT_FOUND}), 404

    buffer = BytesIO()
    verification_url = url_for(
        "web.verify_certificate_view",
        code=qr_code_value,
        _external=True,
    )
    image = qrcode.make(verification_url)
    image.save(buffer, format="PNG")
    buffer.seek(0)
    return send_file(buffer, mimetype="image/png")
