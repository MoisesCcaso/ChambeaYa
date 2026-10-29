from flask import Blueprint, current_app, jsonify, session

from application.notificacion_application_service import NotificacionApplicationService
from application.postulacion_application_service import PostulacionApplicationService
from infrastructure.sqlalchemy_notificacion_repository import SqlAlchemyNotificacionRepository
from infrastructure.sqlalchemy_postulacion_repository import SqlAlchemyPostulacionRepository
from infrastructure.sqlalchemy_convocatoria_repository import SqlAlchemyConvocatoriaRepository
from infrastructure.sqlalchemy_perfil_repository import SqlAlchemyPerfilRepository
from infrastructure.sqlalchemy_practica_repository import SqlAlchemyPracticaRepository
from presentation.postulacion_controller import PostulacionController


postulacion_bp = Blueprint("postulacion", __name__, url_prefix="/postulaciones")


def build_postulacion_controller():
    postulacion_repository = SqlAlchemyPostulacionRepository()
    convocatoria_repository = SqlAlchemyConvocatoriaRepository()
    perfil_repository = SqlAlchemyPerfilRepository()
    service = PostulacionApplicationService(
        postulacion_repository,
        convocatoria_repository,
        perfil_repository,
        SqlAlchemyPracticaRepository(),
    )
    return PostulacionController(service)


def get_authenticated_user_id():
    return session.get("usuario_id")


def get_authenticated_empresa():
    usuario_id = get_authenticated_user_id()
    if usuario_id is None:
        return None
    return SqlAlchemyPerfilRepository().find_empresa_by_user_id(usuario_id)


@postulacion_bp.post("/convocatorias/<int:convocatoria_id>")
def apply_to_convocatoria(convocatoria_id):
    usuario_id = get_authenticated_user_id()
    if usuario_id is None:
        return jsonify({"error": "No autenticado"}), 401
    try:
        data, status_code = build_postulacion_controller().postular(
            usuario_id, convocatoria_id
        )
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    return jsonify(data), status_code


@postulacion_bp.get("/me")
def list_my_postulaciones():
    usuario_id = get_authenticated_user_id()
    if usuario_id is None:
        return jsonify({"error": "No autenticado"}), 401
    try:
        data, status_code = build_postulacion_controller().list_mine(usuario_id)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    return jsonify(data), status_code


@postulacion_bp.get("/convocatorias/<int:convocatoria_id>")
def list_convocatoria_postulaciones(convocatoria_id):
    empresa = get_authenticated_empresa()
    if get_authenticated_user_id() is None:
        return jsonify({"error": "No autenticado"}), 401
    if empresa is None:
        return jsonify({"error": "Empresa no encontrada para este usuario"}), 400
    try:
        data, status_code = build_postulacion_controller().list_for_convocatoria(
            empresa.id, convocatoria_id
        )
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    return jsonify(data), status_code


@postulacion_bp.post("/<int:postulacion_id>/seleccionar")
def select_postulacion(postulacion_id):
    usuario_id = get_authenticated_user_id()
    if usuario_id is None:
        return jsonify({"error": "No autenticado"}), 401

    perfil_repository = SqlAlchemyPerfilRepository()
    empresa = perfil_repository.find_empresa_by_user_id(usuario_id)
    if empresa is None:
        return jsonify({"error": "Empresa no encontrada para este usuario"}), 400

    postulacion_repository = SqlAlchemyPostulacionRepository()
    objetivo = postulacion_repository.find_by_id(postulacion_id)
    otras_pendientes = []
    if objetivo is not None:
        otras_pendientes = [
            item
            for item in postulacion_repository.find_by_convocatoria_id(
                objetivo.convocatoria_id
            )
            if item.id != postulacion_id
            and item.estado in ("pendiente", "seleccionada")
        ]

    controller = build_postulacion_controller()
    try:
        data, status_code = controller.select(empresa.id, postulacion_id)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    if status_code == 200:
        try:
            repo = SqlAlchemyNotificacionRepository()
            notif_service = NotificacionApplicationService(writer=repo, reader=repo)
            perfil_repo = SqlAlchemyPerfilRepository()
            practicante = perfil_repo.find_practicante_by_id(data["practicante_id"])
            if practicante:
                notif_service.create_notification(
                    usuario_destino_id=practicante.usuario_id,
                    tipo="POSTULACION_SELECCIONADA",
                    mensaje="Has sido seleccionado para una convocatoria",
                    metadata={"postulacion_id": postulacion_id},
                )
            for rechazada in otras_pendientes:
                otro_practicante = perfil_repo.find_practicante_by_id(
                    rechazada.practicante_id
                )
                if otro_practicante:
                    notif_service.create_notification(
                        usuario_destino_id=otro_practicante.usuario_id,
                        tipo="POSTULACION_RECHAZADA",
                        mensaje="Tu postulación no fue seleccionada",
                        metadata={"postulacion_id": rechazada.id},
                    )
        except Exception:
            current_app.logger.exception(
                "No se pudo crear la notificación de postulación seleccionada"
            )

    return jsonify(data), status_code


@postulacion_bp.post("/<int:postulacion_id>/rechazar")
def reject_postulacion(postulacion_id):
    usuario_id = get_authenticated_user_id()
    if usuario_id is None:
        return jsonify({"error": "No autenticado"}), 401

    empresa = get_authenticated_empresa()
    if empresa is None:
        return jsonify({"error": "Empresa no encontrada para este usuario"}), 400

    controller = build_postulacion_controller()
    try:
        data, status_code = controller.reject(empresa.id, postulacion_id)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    practicante = SqlAlchemyPerfilRepository().find_practicante_by_id(
        data["practicante_id"]
    )
    if practicante:
        repo = SqlAlchemyNotificacionRepository()
        NotificacionApplicationService(writer=repo, reader=repo).create_notification(
            usuario_destino_id=practicante.usuario_id,
            tipo="POSTULACION_RECHAZADA",
            mensaje="Tu postulación no fue seleccionada",
            metadata={"postulacion_id": postulacion_id},
        )
    return jsonify(data), status_code


@postulacion_bp.post("/<int:postulacion_id>/cancelar")
def cancel_postulacion(postulacion_id):
    usuario_id = get_authenticated_user_id()
    if usuario_id is None:
        return jsonify({"error": "No autenticado"}), 401
    try:
        data, status_code = build_postulacion_controller().cancel(
            usuario_id, postulacion_id
        )
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    return jsonify(data), status_code


@postulacion_bp.post("/<int:postulacion_id>/reconsiderar")
def reconsider_postulacion(postulacion_id):
    usuario_id = get_authenticated_user_id()
    if usuario_id is None:
        return jsonify({"error": "No autenticado"}), 401
    empresa = get_authenticated_empresa()
    if empresa is None:
        return jsonify({"error": "Empresa no encontrada para este usuario"}), 400
    try:
        data, status_code = build_postulacion_controller().reconsider(
            empresa.id, postulacion_id
        )
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    try:
        practicante = SqlAlchemyPerfilRepository().find_practicante_by_id(
            data["practicante_id"]
        )
        if practicante:
            repo = SqlAlchemyNotificacionRepository()
            NotificacionApplicationService(writer=repo, reader=repo).create_notification(
                usuario_destino_id=practicante.usuario_id,
                tipo="POSTULACION_RECONSIDERADA",
                mensaje="La empresa volvió a considerar tu postulación",
                metadata={"postulacion_id": postulacion_id},
            )
    except Exception:
        current_app.logger.exception(
            "No se pudo crear la notificación de postulación reconsiderada"
        )
    return jsonify(data), status_code
