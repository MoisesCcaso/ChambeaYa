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

from application.notificacion_application_service import NotificacionApplicationService
from frameworks.flask_mvc.dependencies import container


practica_bp = Blueprint("practica", __name__, url_prefix="/practicas")
NO_AUTENTICADO_ERROR = "No autenticado"


def build_practica_service():
    return container.get_practica_service()


def serialize_practica(practica):
    return {
        "id": practica.id,
        "postulacion_id": practica.postulacion_id,
        "practicante_id": practica.practicante_id,
        "estado": practica.estado,
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


def get_authenticated_empresa():
    usuario_id = get_authenticated_user_id()
    if usuario_id is None:
        return None
    return container.get_perfil_repository().find_empresa_by_user_id(usuario_id)


@practica_bp.post("")
def start_practica():
    usuario_id = get_authenticated_user_id()
    if usuario_id is None:
        return jsonify({"error": NO_AUTENTICADO_ERROR}), 401
    empresa = get_authenticated_empresa()
    if empresa is None:
        return jsonify({"error": "Empresa no encontrada para este usuario"}), 400

    postulacion_id = (request.get_json(silent=True) or {}).get("postulacion_id")
    try:
        practica = build_practica_service().start_practica(empresa.id, postulacion_id)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    return jsonify(serialize_practica(practica)), 201


@practica_bp.get("")
def list_practicas():
    usuario_id = get_authenticated_user_id()
    if usuario_id is None:
        return jsonify({"error": NO_AUTENTICADO_ERROR}), 401
    try:
        practicas = build_practica_service().list_for_user(usuario_id)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    return jsonify([serialize_practica(item) for item in practicas]), 200


@practica_bp.get("/<int:practica_id>")
def get_practica(practica_id):
    usuario_id = get_authenticated_user_id()
    if usuario_id is None:
        return jsonify({"error": NO_AUTENTICADO_ERROR}), 401
    try:
        practica = build_practica_service().get_for_user(usuario_id, practica_id)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    return jsonify(serialize_practica(practica)), 200


@practica_bp.post("/<int:practica_id>/evaluar")
def register_evaluation(practica_id):
    usuario_id = get_authenticated_user_id()
    if usuario_id is None:
        return jsonify({"error": NO_AUTENTICADO_ERROR}), 401

    empresa = get_authenticated_empresa()
    if empresa is None:
        return jsonify({"error": "Empresa no encontrada para este usuario"}), 400

    payload = request.get_json(silent=True) or {}
    try:
        practica = build_practica_service().evaluate(empresa.id, practica_id, payload.get("puntaje"))
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    data = serialize_practica(practica)
    return jsonify(data), 201


@practica_bp.post("/<int:practica_id>/entregables")
def upload_deliverable(practica_id):
    usuario_id = get_authenticated_user_id()
    if usuario_id is None:
        return jsonify({"error": NO_AUTENTICADO_ERROR}), 401

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
        try:
            service.get_for_user(usuario_id, practica_id)
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400
        nombre_guardado = f"{uuid4().hex}_{nombre_seguro}"
        ruta_guardada = Path(current_app.config["UPLOAD_FOLDER"]) / nombre_guardado
        archivo_subido.save(ruta_guardada)
        payload = {"archivo": nombre_guardado}
    else:
        payload = request.get_json(silent=True) or {}

    try:
        practica = service.upload_deliverable(usuario_id, practica_id, payload.get("archivo"))
    except ValueError as exc:
        if ruta_guardada is not None and ruta_guardada.is_file():
            ruta_guardada.unlink()
        return jsonify({"error": str(exc)}), 400

    return jsonify(serialize_practica(practica)), 201


@practica_bp.get("/<int:practica_id>/entregables")
def get_deliverables_history(practica_id):
    usuario_id = get_authenticated_user_id()
    if usuario_id is None:
        return jsonify({"error": NO_AUTENTICADO_ERROR}), 401

    try:
        entregables = build_practica_service().get_deliverables_history(usuario_id, practica_id)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify([serialize_entregable(e) for e in entregables]), 200


@practica_bp.get("/<int:practica_id>/evaluaciones")
def get_evaluations_history(practica_id):
    usuario_id = get_authenticated_user_id()
    if usuario_id is None:
        return jsonify({"error": NO_AUTENTICADO_ERROR}), 401

    try:
        evaluaciones = build_practica_service().get_evaluations_history(usuario_id, practica_id)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify([serialize_evaluacion(e) for e in evaluaciones]), 200


@practica_bp.delete(
    "/<int:practica_id>/entregables/<int:entregable_id>"
)
def delete_deliverable(practica_id, entregable_id):
    usuario_id = get_authenticated_user_id()
    if usuario_id is None:
        return jsonify({"error": NO_AUTENTICADO_ERROR}), 401
    try:
        data = serialize_entregable(
            build_practica_service().delete_deliverable(usuario_id, practica_id, entregable_id)
        )
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    nombre = Path(data["archivo"]).name
    ruta = Path(current_app.config["UPLOAD_FOLDER"]) / nombre
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
    usuario_id = get_authenticated_user_id()
    if usuario_id is None:
        return jsonify({"error": NO_AUTENTICADO_ERROR}), 401
    empresa = get_authenticated_empresa()
    if empresa is None:
        return jsonify({"error": "Empresa no encontrada para este usuario"}), 400
    try:
        data = serialize_evaluacion(
            build_practica_service().delete_evaluation(empresa.id, practica_id, evaluacion_id)
        )
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    return jsonify(data), 200


@practica_bp.get(
    "/<int:practica_id>/entregables/<int:entregable_id>/archivo"
)
def download_deliverable(practica_id, entregable_id):
    usuario_id = get_authenticated_user_id()
    if usuario_id is None:
        return jsonify({"error": NO_AUTENTICADO_ERROR}), 401
    try:
        entregables = build_practica_service().get_deliverables_history(usuario_id, practica_id)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    entregable = next((item for item in entregables if item.id == entregable_id), None)
    if entregable is None:
        return jsonify({"error": "Entregable no encontrado"}), 404
    nombre = Path(entregable.archivo).name
    ruta = Path(current_app.config["UPLOAD_FOLDER"]) / nombre
    if not ruta.is_file():
        return jsonify({"error": "Archivo de entregable no encontrado"}), 404
    return send_from_directory(
        current_app.config["UPLOAD_FOLDER"],
        nombre,
        as_attachment=True,
    )


@practica_bp.post("/<int:practica_id>/finalizar")
def finish_practica(practica_id):
    usuario_id = get_authenticated_user_id()
    if usuario_id is None:
        return jsonify({"error": NO_AUTENTICADO_ERROR}), 401
    empresa = get_authenticated_empresa()
    if empresa is None:
        return jsonify({"error": "Empresa no encontrada para este usuario"}), 400

    try:
        data = serialize_practica(build_practica_service().finish(empresa.id, practica_id))
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    return jsonify(data), 200
