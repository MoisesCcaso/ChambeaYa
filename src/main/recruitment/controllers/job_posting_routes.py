from flask import Blueprint, jsonify, request, session

from bootstrap.dependencies import container
from shared.http_messages import NOT_AUTHENTICATED, COMPANY_NOT_FOUND


job_posting_bp = Blueprint("convocatoria", __name__, url_prefix="/convocatorias")


def build_job_posting_service():
    return container.get_job_posting_service()


def get_authenticated_company(user_id):
    if user_id is None:
        return None
    return container.get_profiles_api().find_company_by_user_id(user_id)


def serialize_job_posting(job_posting):
    return {
        "id": job_posting.id,
        "empresa_id": job_posting.company_id,
        "titulo": job_posting.title,
        "descripcion": job_posting.description,
        "estado": job_posting.status,
        "habilidades_requeridas": job_posting.required_skills,
        "beneficios": job_posting.benefits,
        "fecha_publicacion": (
            job_posting.published_at.isoformat()
            if job_posting.published_at
            else None
        ),
        "fecha_cierre": (
            job_posting.closing_date.isoformat()
            if job_posting.closing_date
            else None
        ),
    }


def get_authenticated_user_id():
    return session.get("usuario_id")


@job_posting_bp.get("")
def list_job_postings():
    job_postings = build_job_posting_service().search(request.args.get("q"), "publicada")
    return jsonify([serialize_job_posting(item) for item in job_postings]), 200


@job_posting_bp.get("/mis")
def list_my_job_postings():
    user_id = get_authenticated_user_id()
    if user_id is None:
        return jsonify({"error": NOT_AUTHENTICATED}), 401
    company = get_authenticated_company(user_id)
    if company is None:
        return jsonify({"error": COMPANY_NOT_FOUND}), 403
    job_postings = build_job_posting_service().list_for_company(company.id)
    return jsonify([serialize_job_posting(item) for item in job_postings]), 200


@job_posting_bp.get("/<int:job_posting_id>")
def get_job_posting(job_posting_id):
    data = serialize_job_posting(build_job_posting_service().find_by_id(job_posting_id))
    if data["estado"] != "publicada":
        user_id = get_authenticated_user_id()
        company = get_authenticated_company(user_id)
        if company is None or company.id != data["empresa_id"]:
            return jsonify({"error": "Convocatoria no encontrada"}), 404
    return jsonify(data), 200


@job_posting_bp.post("")
def create_job_posting():
    user_id = get_authenticated_user_id()
    if user_id is None:
        return jsonify({"error": NOT_AUTHENTICATED}), 401

    company = get_authenticated_company(user_id)
    if company is None:
        return jsonify({"error": COMPANY_NOT_FOUND}), 403
    if not company.verified:
        return jsonify({"error": "La empresa debe estar verificada"}), 403

    payload = request.get_json(silent=True) or {}
    job_posting = build_job_posting_service().create_job_posting(company.id, payload)

    return jsonify(serialize_job_posting(job_posting)), 201

@job_posting_bp.post("/<int:job_posting_id>/publicar")
def publish_job_posting(job_posting_id):
    user_id = get_authenticated_user_id()
    if user_id is None:
        return jsonify({"error": NOT_AUTHENTICATED}), 401

    company = get_authenticated_company(user_id)
    if company is None:
        return jsonify({"error": COMPANY_NOT_FOUND}), 403

    job_posting = build_job_posting_service().publish(company.id, job_posting_id)

    return jsonify(serialize_job_posting(job_posting)), 200


@job_posting_bp.put("/<int:job_posting_id>")
def update_job_posting(job_posting_id):
    user_id = get_authenticated_user_id()
    if user_id is None:
        return jsonify({"error": NOT_AUTHENTICATED}), 401
    company = get_authenticated_company(user_id)
    if company is None:
        return jsonify({"error": COMPANY_NOT_FOUND}), 403
    job_posting = build_job_posting_service().update(
        company.id,
        job_posting_id,
        request.get_json(silent=True) or {},
    )
    return jsonify(serialize_job_posting(job_posting)), 200


@job_posting_bp.post("/<int:job_posting_id>/cerrar")
def close_job_posting(job_posting_id):
    user_id = get_authenticated_user_id()
    if user_id is None:
        return jsonify({"error": NOT_AUTHENTICATED}), 401

    company = get_authenticated_company(user_id)
    if company is None:
        return jsonify({"error": COMPANY_NOT_FOUND}), 403

    job_posting = build_job_posting_service().close(company.id, job_posting_id)
    return jsonify(serialize_job_posting(job_posting)), 200


@job_posting_bp.post("/<int:job_posting_id>/reabrir")
def reopen_job_posting(job_posting_id):
    user_id = get_authenticated_user_id()
    if user_id is None:
        return jsonify({"error": NOT_AUTHENTICATED}), 401
    company = get_authenticated_company(user_id)
    if company is None:
        return jsonify({"error": COMPANY_NOT_FOUND}), 403
    job_posting = build_job_posting_service().reopen(company.id, job_posting_id)
    return jsonify(serialize_job_posting(job_posting)), 200


@job_posting_bp.post("/<int:job_posting_id>/duplicar")
def duplicate_job_posting(job_posting_id):
    user_id = get_authenticated_user_id()
    if user_id is None:
        return jsonify({"error": NOT_AUTHENTICATED}), 401
    company = get_authenticated_company(user_id)
    if company is None:
        return jsonify({"error": COMPANY_NOT_FOUND}), 403
    job_posting = build_job_posting_service().duplicate(company.id, job_posting_id)
    return jsonify(serialize_job_posting(job_posting)), 201


@job_posting_bp.delete("/<int:job_posting_id>")
def delete_job_posting(job_posting_id):
    user_id = get_authenticated_user_id()
    if user_id is None:
        return jsonify({"error": NOT_AUTHENTICATED}), 401
    company = get_authenticated_company(user_id)
    if company is None:
        return jsonify({"error": COMPANY_NOT_FOUND}), 403
    job_posting = build_job_posting_service().delete(company.id, job_posting_id)
    return jsonify({"id": job_posting.id, "mensaje": "Convocatoria eliminada"}), 200
