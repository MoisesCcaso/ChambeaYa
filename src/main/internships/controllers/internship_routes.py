from pathlib import Path
from uuid import uuid4

from flask import (
    Blueprint,
    current_app,
    jsonify,
    request,
    send_from_directory,
    session,
)
from werkzeug.utils import secure_filename

from bootstrap.dependencies import container
from shared.http_messages import NOT_AUTHENTICATED, COMPANY_NOT_FOUND


internship_bp = Blueprint("practica", __name__, url_prefix="/practicas")


def build_internship_service():
    return container.get_internship_service()


def serialize_internship(internship):
    return {
        "id": internship.id,
        "postulacion_id": internship.job_application_id,
        "practicante_id": internship.intern_id,
        "estado": internship.status,
    }


def serialize_deliverable(deliverable):
    return {
        "id": deliverable.id,
        "practica_id": deliverable.internship_id,
        "archivo": deliverable.file_name,
        "fecha_subida": deliverable.uploaded_at.isoformat() if deliverable.uploaded_at else None,
        "archivo_url": (
            f"/practicas/{deliverable.internship_id}/entregables/"
            f"{deliverable.id}/archivo"
            if deliverable.id is not None
            else None
        ),
    }


def serialize_evaluation(evaluation):
    return {
        "id": evaluation.id,
        "practica_id": evaluation.internship_id,
        "puntaje": evaluation.score,
        "fecha_evaluacion": evaluation.evaluated_at.isoformat() if evaluation.evaluated_at else None,
        "aprobada": evaluation.is_approved(),
    }


def get_authenticated_user_id():
    return session.get("usuario_id")


def get_authenticated_company():
    user_id = get_authenticated_user_id()
    if user_id is None:
        return None
    return container.get_profiles_api().find_company_by_user_id(user_id)


@internship_bp.post("")
def start_internship():
    user_id = get_authenticated_user_id()
    if user_id is None:
        return jsonify({"error": NOT_AUTHENTICATED}), 401
    company = get_authenticated_company()
    if company is None:
        return jsonify({"error": COMPANY_NOT_FOUND}), 403

    job_application_id = (request.get_json(silent=True) or {}).get("postulacion_id")
    internship = build_internship_service().start_internship(company.id, job_application_id)
    return jsonify(serialize_internship(internship)), 201


@internship_bp.get("")
def list_internships():
    user_id = get_authenticated_user_id()
    if user_id is None:
        return jsonify({"error": NOT_AUTHENTICATED}), 401
    internship_list = build_internship_service().list_for_user(user_id)
    return jsonify([serialize_internship(item) for item in internship_list]), 200


@internship_bp.get("/<int:internship_id>")
def get_internship(internship_id):
    user_id = get_authenticated_user_id()
    if user_id is None:
        return jsonify({"error": NOT_AUTHENTICATED}), 401
    internship = build_internship_service().get_for_user(user_id, internship_id)
    return jsonify(serialize_internship(internship)), 200


@internship_bp.post("/<int:internship_id>/evaluar")
def register_evaluation(internship_id):
    user_id = get_authenticated_user_id()
    if user_id is None:
        return jsonify({"error": NOT_AUTHENTICATED}), 401

    company = get_authenticated_company()
    if company is None:
        return jsonify({"error": COMPANY_NOT_FOUND}), 403

    payload = request.get_json(silent=True) or {}
    internship = build_internship_service().evaluate(company.id, internship_id, payload.get("puntaje"))
    data = serialize_internship(internship)
    return jsonify(data), 201


@internship_bp.post("/<int:internship_id>/entregables")
def upload_deliverable(internship_id):
    user_id = get_authenticated_user_id()
    if user_id is None:
        return jsonify({"error": NOT_AUTHENTICATED}), 401

    service = build_internship_service()
    uploaded_file = request.files.get("archivo")
    saved_path = None
    if uploaded_file is not None:
        safe_name = secure_filename(uploaded_file.filename or "")
        extension = Path(safe_name).suffix.lower()
        if not safe_name or extension not in {".pdf", ".doc", ".docx", ".zip"}:
            return jsonify(
                {"error": "El entregable debe ser PDF, DOC, DOCX o ZIP"}
            ), 400
        service.get_for_user(user_id, internship_id)
        stored_name = f"{uuid4().hex}_{safe_name}"
        saved_path = Path(current_app.config["UPLOAD_FOLDER"]) / stored_name
        uploaded_file.save(saved_path)
        payload = {"archivo": stored_name}
    else:
        payload = request.get_json(silent=True) or {}

    try:
        internship = service.upload_deliverable(user_id, internship_id, payload.get("archivo"))
    except ValueError:
        if saved_path is not None and saved_path.is_file():
            saved_path.unlink()
        raise

    return jsonify(serialize_internship(internship)), 201


@internship_bp.get("/<int:internship_id>/entregables")
def get_deliverables_history(internship_id):
    user_id = get_authenticated_user_id()
    if user_id is None:
        return jsonify({"error": NOT_AUTHENTICATED}), 401

    deliverables = build_internship_service().get_deliverables_history(user_id, internship_id)

    return jsonify([serialize_deliverable(e) for e in deliverables]), 200


@internship_bp.get("/<int:internship_id>/evaluaciones")
def get_evaluations_history(internship_id):
    user_id = get_authenticated_user_id()
    if user_id is None:
        return jsonify({"error": NOT_AUTHENTICATED}), 401

    evaluations = build_internship_service().get_evaluations_history(user_id, internship_id)

    return jsonify([serialize_evaluation(e) for e in evaluations]), 200


@internship_bp.delete(
    "/<int:internship_id>/entregables/<int:deliverable_id>"
)
def delete_deliverable(internship_id, deliverable_id):
    user_id = get_authenticated_user_id()
    if user_id is None:
        return jsonify({"error": NOT_AUTHENTICATED}), 401
    data = serialize_deliverable(
        build_internship_service().delete_deliverable(user_id, internship_id, deliverable_id)
    )

    name = Path(data["archivo"]).name
    file_path = Path(current_app.config["UPLOAD_FOLDER"]) / name
    try:
        if file_path.is_file():
            file_path.unlink()
    except OSError:
        current_app.logger.exception(
            "El entregable fue eliminado, pero no se pudo borrar su archivo"
        )
    return jsonify(data), 200


@internship_bp.delete(
    "/<int:internship_id>/evaluaciones/<int:evaluation_id>"
)
def delete_evaluation(internship_id, evaluation_id):
    user_id = get_authenticated_user_id()
    if user_id is None:
        return jsonify({"error": NOT_AUTHENTICATED}), 401
    company = get_authenticated_company()
    if company is None:
        return jsonify({"error": COMPANY_NOT_FOUND}), 403
    data = serialize_evaluation(
        build_internship_service().delete_evaluation(company.id, internship_id, evaluation_id)
    )
    return jsonify(data), 200


@internship_bp.get(
    "/<int:internship_id>/entregables/<int:deliverable_id>/archivo"
)
def download_deliverable(internship_id, deliverable_id):
    user_id = get_authenticated_user_id()
    if user_id is None:
        return jsonify({"error": NOT_AUTHENTICATED}), 401
    deliverables = build_internship_service().get_deliverables_history(user_id, internship_id)

    deliverable = next((item for item in deliverables if item.id == deliverable_id), None)
    if deliverable is None:
        return jsonify({"error": "Entregable no encontrado"}), 404
    name = Path(deliverable.file_name).name
    file_path = Path(current_app.config["UPLOAD_FOLDER"]) / name
    if not file_path.is_file():
        return jsonify({"error": "Archivo de entregable no encontrado"}), 404
    return send_from_directory(
        current_app.config["UPLOAD_FOLDER"],
        name,
        as_attachment=True,
    )


@internship_bp.post("/<int:internship_id>/finalizar")
def finish_internship(internship_id):
    user_id = get_authenticated_user_id()
    if user_id is None:
        return jsonify({"error": NOT_AUTHENTICATED}), 401
    company = get_authenticated_company()
    if company is None:
        return jsonify({"error": COMPANY_NOT_FOUND}), 403

    data = serialize_internship(build_internship_service().finish(company.id, internship_id))
    return jsonify(data), 200
