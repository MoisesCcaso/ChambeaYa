from flask import Blueprint, current_app, jsonify, session

from application.notificacion_application_service import NotificacionApplicationService
from application.postulacion_application_service import PostulacionApplicationService
from infrastructure.sqlalchemy_notificacion_repository import SqlAlchemyNotificacionRepository
from infrastructure.sqlalchemy_postulacion_repository import SqlAlchemyPostulacionRepository
from infrastructure.sqlalchemy_convocatoria_repository import SqlAlchemyConvocatoriaRepository
from infrastructure.sqlalchemy_perfil_repository import SqlAlchemyPerfilRepository
from infrastructure.sqlalchemy_practica_repository import SqlAlchemyPracticaRepository


postulacion_bp = Blueprint("postulacion", __name__, url_prefix="/postulaciones")


def build_postulacion_service():
    return PostulacionApplicationService(
        SqlAlchemyPostulacionRepository(),
        SqlAlchemyConvocatoriaRepository(),
        SqlAlchemyPerfilRepository(),
        SqlAlchemyPracticaRepository(),
    )


def serialize_postulacion(postulacion):
    return {
        "id": postulacion.id,
        "convocatoria_id": postulacion.convocatoria_id,
        "practicante_id": postulacion.practicante_id,
        "estado": postulacion.estado,
    }


def serialize_postulacion_con_convocatoria(postulacion, convocatoria):
    item = serialize_postulacion(postulacion)
    item["convocatoria"] = (
        {
            "id": convocatoria.id,
            "titulo": convocatoria.titulo,
            "estado": convocatoria.estado,
        }
        if convocatoria
        else None
    )
    return item


def serialize_candidato(postulacion, practicante, practica):
    item = serialize_postulacion(postulacion)
    item["practicante"] = (
        {
            "id": practicante.id,
            "nombres": practicante.nombres,
            "apellidos": practicante.apellidos,
            "habilidades": practicante.habilidades,
            "score_reputacion": practicante.score_reputacion,
            "identidad_verificada": practicante.identidad_verificada,
        }
        if practicante
        else None
    )
    item["practica_iniciada"] = practica is not None
    return item


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
        postulacion = build_postulacion_service().apply(usuario_id, convocatoria_id)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    return jsonify(serialize_postulacion(postulacion)), 201


@postulacion_bp.get("/me")
def list_my_postulaciones():
    usuario_id = get_authenticated_user_id()
    if usuario_id is None:
        return jsonify({"error": "No autenticado"}), 401
    try:
        resultados = build_postulacion_service().list_for_practicante(usuario_id)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    return jsonify([
        serialize_postulacion_con_convocatoria(r.postulacion, r.convocatoria)
        for r in resultados
    ]), 200


@postulacion_bp.get("/convocatorias/<int:convocatoria_id>")
def list_convocatoria_postulaciones(convocatoria_id):
    empresa = get_authenticated_empresa()
    if get_authenticated_user_id() is None:
        return jsonify({"error": "No autenticado"}), 401
    if empresa is None:
        return jsonify({"error": "Empresa no encontrada para este usuario"}), 400
    try:
        resultados = build_postulacion_service().list_for_convocatoria(
            empresa.id, convocatoria_id
        )
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    return jsonify([
        serialize_candidato(r.postulacion, r.practicante, r.practica)
        for r in resultados
    ]), 200


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

    try:
        postulacion = build_postulacion_service().select_candidate(empresa.id, postulacion_id)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    data = serialize_postulacion(postulacion)

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

    return jsonify(data), 200


@postulacion_bp.post("/<int:postulacion_id>/rechazar")
def reject_postulacion(postulacion_id):
    usuario_id = get_authenticated_user_id()
    if usuario_id is None:
        return jsonify({"error": "No autenticado"}), 401

    empresa = get_authenticated_empresa()
    if empresa is None:
        return jsonify({"error": "Empresa no encontrada para este usuario"}), 400

    try:
        postulacion = build_postulacion_service().reject_candidate(empresa.id, postulacion_id)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    data = serialize_postulacion(postulacion)

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
    return jsonify(data), 200


@postulacion_bp.post("/<int:postulacion_id>/cancelar")
def cancel_postulacion(postulacion_id):
    usuario_id = get_authenticated_user_id()
    if usuario_id is None:
        return jsonify({"error": "No autenticado"}), 401
    try:
        data = serialize_postulacion(
            build_postulacion_service().cancel(usuario_id, postulacion_id)
        )
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    return jsonify(data), 200


@postulacion_bp.post("/<int:postulacion_id>/reconsiderar")
def reconsider_postulacion(postulacion_id):
    usuario_id = get_authenticated_user_id()
    if usuario_id is None:
        return jsonify({"error": "No autenticado"}), 401
    empresa = get_authenticated_empresa()
    if empresa is None:
        return jsonify({"error": "Empresa no encontrada para este usuario"}), 400
    try:
        data = serialize_postulacion(
            build_postulacion_service().reconsider_candidate(empresa.id, postulacion_id)
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
    return jsonify(data), 200
