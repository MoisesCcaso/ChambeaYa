from flask import Blueprint, current_app, jsonify, session

from bootstrap.dependencies import container
from shared.http_messages import NOT_AUTHENTICATED, COMPANY_NOT_FOUND


job_application_bp = Blueprint("postulacion", __name__, url_prefix="/postulaciones")


def build_job_application_service():
    return container.get_job_application_service()


def serialize_job_application(job_application):
    return {
        "id": job_application.id,
        "convocatoria_id": job_application.job_posting_id,
        "practicante_id": job_application.intern_id,
        "estado": job_application.status,
    }


def serialize_job_application_with_posting(job_application, job_posting):
    item = serialize_job_application(job_application)
    item["convocatoria"] = (
        {
            "id": job_posting.id,
            "titulo": job_posting.title,
            "estado": job_posting.status,
        }
        if job_posting
        else None
    )
    return item


def serialize_candidate(job_application, intern, internship):
    item = serialize_job_application(job_application)
    item["practicante"] = (
        {
            "id": intern.id,
            "nombres": intern.first_names,
            "apellidos": intern.last_names,
            "habilidades": intern.skills,
            "score_reputacion": intern.reputation_score,
            "identidad_verificada": intern.identity_verified,
        }
        if intern
        else None
    )
    item["practica_iniciada"] = internship is not None
    return item


def get_authenticated_user_id():
    return session.get("usuario_id")


def get_authenticated_company():
    user_id = get_authenticated_user_id()
    if user_id is None:
        return None
    return container.get_profile_repository().find_company_by_user_id(user_id)


@job_application_bp.post("/convocatorias/<int:job_posting_id>")
def apply_to_job_posting(job_posting_id):
    user_id = get_authenticated_user_id()
    if user_id is None:
        return jsonify({"error": NOT_AUTHENTICATED}), 401
    job_application = build_job_application_service().apply(user_id, job_posting_id)
    return jsonify(serialize_job_application(job_application)), 201


@job_application_bp.get("/me")
def list_my_job_applications():
    user_id = get_authenticated_user_id()
    if user_id is None:
        return jsonify({"error": NOT_AUTHENTICATED}), 401
    results = build_job_application_service().list_for_intern(user_id)
    return jsonify([
        serialize_job_application_with_posting(r.job_application, r.job_posting)
        for r in results
    ]), 200


@job_application_bp.get("/convocatorias/<int:job_posting_id>")
def list_job_posting_applications(job_posting_id):
    company = get_authenticated_company()
    if get_authenticated_user_id() is None:
        return jsonify({"error": NOT_AUTHENTICATED}), 401
    if company is None:
        return jsonify({"error": COMPANY_NOT_FOUND}), 403
    results = build_job_application_service().list_for_job_posting(
        company.id, job_posting_id
    )
    return jsonify([
        serialize_candidate(r.job_application, r.intern, r.internship)
        for r in results
    ]), 200


@job_application_bp.post("/<int:job_application_id>/seleccionar")
def select_job_application(job_application_id):
    user_id = get_authenticated_user_id()
    if user_id is None:
        return jsonify({"error": NOT_AUTHENTICATED}), 401

    company = get_authenticated_company()
    if company is None:
        return jsonify({"error": COMPANY_NOT_FOUND}), 403

    job_application = build_job_application_service().select_candidate(company.id, job_application_id)

    return jsonify(serialize_job_application(job_application)), 200


@job_application_bp.post("/<int:job_application_id>/rechazar")
def reject_job_application(job_application_id):
    user_id = get_authenticated_user_id()
    if user_id is None:
        return jsonify({"error": NOT_AUTHENTICATED}), 401

    company = get_authenticated_company()
    if company is None:
        return jsonify({"error": COMPANY_NOT_FOUND}), 403

    job_application = build_job_application_service().reject_candidate(company.id, job_application_id)
    data = serialize_job_application(job_application)

    intern = container.get_profile_repository().find_intern_by_id(
        data["practicante_id"]
    )
    if intern:
        container.get_notification_service().create_notification(
            recipient_user_id=intern.user_id,
            notification_type="POSTULACION_RECHAZADA",
            message="Tu postulación no fue seleccionada",
            metadata={"postulacion_id": job_application_id},
        )
    return jsonify(data), 200


@job_application_bp.post("/<int:job_application_id>/cancelar")
def cancel_job_application(job_application_id):
    user_id = get_authenticated_user_id()
    if user_id is None:
        return jsonify({"error": NOT_AUTHENTICATED}), 401
    data = serialize_job_application(
        build_job_application_service().cancel(user_id, job_application_id)
    )
    return jsonify(data), 200


@job_application_bp.post("/<int:job_application_id>/reconsiderar")
def reconsider_job_application(job_application_id):
    user_id = get_authenticated_user_id()
    if user_id is None:
        return jsonify({"error": NOT_AUTHENTICATED}), 401
    company = get_authenticated_company()
    if company is None:
        return jsonify({"error": COMPANY_NOT_FOUND}), 403
    data = serialize_job_application(
        build_job_application_service().reconsider_candidate(company.id, job_application_id)
    )
    try:
        intern = container.get_profile_repository().find_intern_by_id(
            data["practicante_id"]
        )
        if intern:
            container.get_notification_service().create_notification(
                recipient_user_id=intern.user_id,
                notification_type="POSTULACION_RECONSIDERADA",
                message="La empresa volvió a considerar tu postulación",
                metadata={"postulacion_id": job_application_id},
            )
    except Exception:
        current_app.logger.exception(
            "No se pudo crear la notificación de postulación reconsiderada"
        )
    return jsonify(data), 200
