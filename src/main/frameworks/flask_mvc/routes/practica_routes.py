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


practica_bp = Blueprint("practica", __name__, url_prefix="/practicas")


def build_practica_service():
    return container.get_practica_service()


def serialize_practica(practica):
    return {
        "id": practica.id,
        "postulacion_id": practica.job_application_id,
        "practicante_id": practica.intern_id,
        "estado": practica.status,
    }


def serialize_entregable(entregable):
    return {
        "id": entregable.id,
        "practica_id": entregable.practica_id,
        "archivo": entregable.archivo,
        "fecha_subida": entregable.fecha_subida.isoformat() if entregable.fecha_subida else None,
        "archivo_url": (
            f"/practicas/{entregable.practica_id}/entregables/"
            f"{entregable.id}/archivo"
            if entregable.id is not None
            else None
        ),
    }


def serialize_evaluacion(evaluacion):
    return {
        "id": evaluacion.id,
        "practica_id": evaluacion.practica_id,
        "puntaje": evaluacion.puntaje,
        "fecha_evaluacion": evaluacion.fecha_evaluacion.isoformat() if evaluacion.fecha_evaluacion else None,
        "aprobada": evaluacion.esta_aprobada(),
    }


def get_authenticated_user_id():
    return session.get("usuario_id")


def get_authenticated_company():
    user_id = get_authenticated_user_id()
    if user_id is None:
        return None
    return container.get_profile_repository().find_company_by_user_id(user_id)


@practica_bp.post("")
def start_practica():
    user_id = get_authenticated_user_id()
    if user_id is None:
        return jsonify({"error": NOT_AUTHENTICATED}), 401
    company = get_authenticated_company()
    if company is None:
        return jsonify({"error": COMPANY_NOT_FOUND}), 403

    job_application_id = (request.get_json(silent=True) or {}).get("postulacion_id")
    practica = build_practica_service().start_practica(company.id, job_application_id)
    return jsonify(serialize_practica(practica)), 201


@practica_bp.get("")
def list_practicas():
    user_id = get_authenticated_user_id()
    if user_id is None:
        return jsonify({"error": NOT_AUTHENTICATED}), 401
    practicas = build_practica_service().list_for_user(user_id)
    return jsonify([serialize_practica(item) for item in practicas]), 200


@practica_bp.get("/<int:practica_id>")
def get_practica(practica_id):
    user_id = get_authenticated_user_id()
    if user_id is None:
        return jsonify({"error": NOT_AUTHENTICATED}), 401
    practica = build_practica_service().get_for_user(user_id, practica_id)
    return jsonify(serialize_practica(practica)), 200


@practica_bp.post("/<int:practica_id>/evaluar")
def register_evaluation(practica_id):
    user_id = get_authenticated_user_id()
    if user_id is None:
        return jsonify({"error": NOT_AUTHENTICATED}), 401

    company = get_authenticated_company()
    if company is None:
        return jsonify({"error": COMPANY_NOT_FOUND}), 403

    payload = request.get_json(silent=True) or {}
    practica = build_practica_service().evaluate(company.id, practica_id, payload.get("puntaje"))
    data = serialize_practica(practica)
    return jsonify(data), 201


@practica_bp.post("/<int:practica_id>/entregables")
def upload_deliverable(practica_id):
    user_id = get_authenticated_user_id()
    if user_id is None:
        return jsonify({"error": NOT_AUTHENTICATED}), 401

    service = build_practica_service()
    archivo_subido = request.files.get("archivo")
    ruta_guardada = None
    if archivo_subido is not None:
        nombre_seguro = secure_filename(archivo_subido.filename or "")
        extension = Path(nombre_seguro).suffix.lower()
        if not nombre_seguro or extension not in {".pdf", ".doc", ".docx", ".zip"}:
            return jsonify(
                {"error": "El entregable debe ser PDF, DOC, DOCX o ZIP"}
            ), 400
        service.get_for_user(user_id, practica_id)
        nombre_guardado = f"{uuid4().hex}_{nombre_seguro}"
        ruta_guardada = Path(current_app.config["UPLOAD_FOLDER"]) / nombre_guardado
        archivo_subido.save(ruta_guardada)
        payload = {"archivo": nombre_guardado}
    else:
        payload = request.get_json(silent=True) or {}

    try:
        practica = service.upload_deliverable(user_id, practica_id, payload.get("archivo"))
    except ValueError:
        if ruta_guardada is not None and ruta_guardada.is_file():
            ruta_guardada.unlink()
        raise

    return jsonify(serialize_practica(practica)), 201


@practica_bp.get("/<int:practica_id>/entregables")
def get_deliverables_history(practica_id):
    user_id = get_authenticated_user_id()
    if user_id is None:
        return jsonify({"error": NOT_AUTHENTICATED}), 401

    entregables = build_practica_service().get_deliverables_history(user_id, practica_id)

    return jsonify([serialize_entregable(e) for e in entregables]), 200


@practica_bp.get("/<int:practica_id>/evaluaciones")
def get_evaluations_history(practica_id):
    user_id = get_authenticated_user_id()
    if user_id is None:
        return jsonify({"error": NOT_AUTHENTICATED}), 401

    evaluaciones = build_practica_service().get_evaluations_history(user_id, practica_id)

    return jsonify([serialize_evaluacion(e) for e in evaluaciones]), 200


@practica_bp.delete(
    "/<int:practica_id>/entregables/<int:entregable_id>"
)
def delete_deliverable(practica_id, entregable_id):
    user_id = get_authenticated_user_id()
    if user_id is None:
        return jsonify({"error": NOT_AUTHENTICATED}), 401
    data = serialize_entregable(
        build_practica_service().delete_deliverable(user_id, practica_id, entregable_id)
    )

    name = Path(data["archivo"]).name
    ruta = Path(current_app.config["UPLOAD_FOLDER"]) / name
    try:
        if ruta.is_file():
            ruta.unlink()
    except OSError:
        current_app.logger.exception(
            "El entregable fue eliminado, pero no se pudo borrar su archivo"
        )
    return jsonify(data), 200


@practica_bp.delete(
    "/<int:practica_id>/evaluaciones/<int:evaluacion_id>"
)
def delete_evaluation(practica_id, evaluacion_id):
    user_id = get_authenticated_user_id()
    if user_id is None:
        return jsonify({"error": NOT_AUTHENTICATED}), 401
    company = get_authenticated_company()
    if company is None:
        return jsonify({"error": COMPANY_NOT_FOUND}), 403
    data = serialize_evaluacion(
        build_practica_service().delete_evaluation(company.id, practica_id, evaluacion_id)
    )
    return jsonify(data), 200


@practica_bp.get(
    "/<int:practica_id>/entregables/<int:entregable_id>/archivo"
)
def download_deliverable(practica_id, entregable_id):
    user_id = get_authenticated_user_id()
    if user_id is None:
        return jsonify({"error": NOT_AUTHENTICATED}), 401
    entregables = build_practica_service().get_deliverables_history(user_id, practica_id)

    entregable = next((item for item in entregables if item.id == entregable_id), None)
    if entregable is None:
        return jsonify({"error": "Entregable no encontrado"}), 404
    name = Path(entregable.archivo).name
    ruta = Path(current_app.config["UPLOAD_FOLDER"]) / name
    if not ruta.is_file():
        return jsonify({"error": "Archivo de entregable no encontrado"}), 404
    return send_from_directory(
        current_app.config["UPLOAD_FOLDER"],
        name,
        as_attachment=True,
    )


@practica_bp.post("/<int:practica_id>/finalizar")
def finish_practica(practica_id):
    user_id = get_authenticated_user_id()
    if user_id is None:
        return jsonify({"error": NOT_AUTHENTICATED}), 401
    company = get_authenticated_company()
    if company is None:
        return jsonify({"error": COMPANY_NOT_FOUND}), 403

    data = serialize_practica(build_practica_service().finish(company.id, practica_id))
    return jsonify(data), 200
