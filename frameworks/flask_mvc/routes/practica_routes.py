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
from application.practica_application_service import PracticaApplicationService
from infrastructure.sqlalchemy_notificacion_repository import SqlAlchemyNotificacionRepository
from infrastructure.sqlalchemy_practica_repository import SqlAlchemyPracticaRepository
from infrastructure.sqlalchemy_perfil_repository import SqlAlchemyPerfilRepository
from infrastructure.sqlalchemy_postulacion_repository import SqlAlchemyPostulacionRepository
from infrastructure.sqlalchemy_convocatoria_repository import SqlAlchemyConvocatoriaRepository
from presentation.practica_controller import PracticaController


practica_bp = Blueprint("practica", __name__, url_prefix="/practicas")
NO_AUTENTICADO_ERROR = "No autenticado"


def build_practica_controller():
    practica_repository = SqlAlchemyPracticaRepository()
    perfil_repository = SqlAlchemyPerfilRepository()
    postulacion_repository = SqlAlchemyPostulacionRepository()
    convocatoria_repository = SqlAlchemyConvocatoriaRepository()
    service = PracticaApplicationService(
        practica_repository, perfil_repository, postulacion_repository, convocatoria_repository
    )
    return PracticaController(service)


def get_authenticated_user_id():
    return session.get("usuario_id")


def get_authenticated_empresa():
    usuario_id = get_authenticated_user_id()
    if usuario_id is None:
        return None
    return SqlAlchemyPerfilRepository().find_empresa_by_user_id(usuario_id)


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
        data, status_code = build_practica_controller().start(
            empresa.id, postulacion_id
        )
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    return jsonify(data), status_code


@practica_bp.get("")
def list_practicas():
    usuario_id = get_authenticated_user_id()
    if usuario_id is None:
        return jsonify({"error": NO_AUTENTICADO_ERROR}), 401
    try:
        data, status_code = build_practica_controller().list_for_user(usuario_id)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    return jsonify(data), status_code


@practica_bp.get("/<int:practica_id>")
def get_practica(practica_id):
    usuario_id = get_authenticated_user_id()
    if usuario_id is None:
        return jsonify({"error": NO_AUTENTICADO_ERROR}), 401
    try:
        data, status_code = build_practica_controller().get_for_user(
            usuario_id, practica_id
        )
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    return jsonify(data), status_code


@practica_bp.post("/<int:practica_id>/evaluar")
def register_evaluation(practica_id):
    usuario_id = get_authenticated_user_id()
    if usuario_id is None:
        return jsonify({"error": NO_AUTENTICADO_ERROR}), 401

    empresa = get_authenticated_empresa()
    if empresa is None:
        return jsonify({"error": "Empresa no encontrada para este usuario"}), 400

    payload = request.get_json(silent=True) or {}
    controller = build_practica_controller()
    try:
        data, status_code = controller.register_evaluation(empresa.id, practica_id, payload)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    if status_code == 201:
        try:
            repo = SqlAlchemyNotificacionRepository()
            notif_service = NotificacionApplicationService(writer=repo, reader=repo)
            perfil_repo = SqlAlchemyPerfilRepository()
            practicante = perfil_repo.find_practicante_by_id(data["practicante_id"])
            if practicante:
                notif_service.create_notification(
                    usuario_destino_id=practicante.usuario_id,
                    tipo="EVALUACION_DISPONIBLE",
                    mensaje="Tu práctica tiene una nueva evaluación disponible",
                    metadata={"practica_id": practica_id},
                )
        except Exception:
            current_app.logger.exception(
                "No se pudo crear la notificación de evaluación disponible"
            )

    return jsonify(data), status_code


@practica_bp.post("/<int:practica_id>/entregables")
def upload_deliverable(practica_id):
    usuario_id = get_authenticated_user_id()
    if usuario_id is None:
        return jsonify({"error": NO_AUTENTICADO_ERROR}), 401

    controller = build_practica_controller()
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
            controller.get_for_user(usuario_id, practica_id)
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400
        nombre_guardado = f"{uuid4().hex}_{nombre_seguro}"
        ruta_guardada = Path(current_app.config["UPLOAD_FOLDER"]) / nombre_guardado
        archivo_subido.save(ruta_guardada)
        payload = {"archivo": nombre_guardado}
    else:
        payload = request.get_json(silent=True) or {}

    try:
        data, status_code = controller.upload_deliverable(usuario_id, practica_id, payload)
    except ValueError as exc:
        if ruta_guardada is not None and ruta_guardada.is_file():
            ruta_guardada.unlink()
        return jsonify({"error": str(exc)}), 400

    return jsonify(data), status_code


@practica_bp.get("/<int:practica_id>/entregables")
def get_deliverables_history(practica_id):
    usuario_id = get_authenticated_user_id()
    if usuario_id is None:
        return jsonify({"error": NO_AUTENTICADO_ERROR}), 401

    controller = build_practica_controller()
    try:
        data, status_code = controller.get_deliverables_history(usuario_id, practica_id)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify(data), status_code


@practica_bp.get("/<int:practica_id>/evaluaciones")
def get_evaluations_history(practica_id):
    usuario_id = get_authenticated_user_id()
    if usuario_id is None:
        return jsonify({"error": NO_AUTENTICADO_ERROR}), 401

    controller = build_practica_controller()
    try:
        data, status_code = controller.get_evaluations_history(usuario_id, practica_id)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify(data), status_code


@practica_bp.delete(
    "/<int:practica_id>/entregables/<int:entregable_id>"
)
def delete_deliverable(practica_id, entregable_id):
    usuario_id = get_authenticated_user_id()
    if usuario_id is None:
        return jsonify({"error": NO_AUTENTICADO_ERROR}), 401
    try:
        data, status_code = build_practica_controller().delete_deliverable(
            usuario_id, practica_id, entregable_id
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
    return jsonify(data), status_code


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
        data, status_code = build_practica_controller().delete_evaluation(
            empresa.id, practica_id, evaluacion_id
        )
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    return jsonify(data), status_code


@practica_bp.get(
    "/<int:practica_id>/entregables/<int:entregable_id>/archivo"
)
def download_deliverable(practica_id, entregable_id):
    usuario_id = get_authenticated_user_id()
    if usuario_id is None:
        return jsonify({"error": NO_AUTENTICADO_ERROR}), 401
    try:
        data, _status_code = build_practica_controller().get_deliverables_history(
            usuario_id, practica_id
        )
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    entregable = next((item for item in data if item["id"] == entregable_id), None)
    if entregable is None:
        return jsonify({"error": "Entregable no encontrado"}), 404
    nombre = Path(entregable["archivo"]).name
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
        data, status_code = build_practica_controller().finish(
            empresa.id, practica_id
        )
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    return jsonify(data), status_code
