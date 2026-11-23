from flask import Blueprint, jsonify, session

from frameworks.flask_mvc.dependencies import container
from frameworks.flask_mvc.routes.mensajes import NO_AUTENTICADO


notificacion_bp = Blueprint("notificacion", __name__, url_prefix="/notificaciones")


def build_notificacion_service():
    return container.get_notificacion_service()


def serialize_notificacion(notificacion):
    return {
        "id": notificacion.id,
        "usuario_destino_id": notificacion.usuario_destino_id,
        "tipo": notificacion.tipo,
        "mensaje": notificacion.mensaje,
        "metadata": notificacion.metadata,
        "leida": notificacion.leida,
        "created_at": notificacion.created_at.isoformat() if notificacion.created_at else None,
    }


def get_authenticated_user_id():
    return session.get("usuario_id")


@notificacion_bp.get("")
def list_notificaciones():
    usuario_id = get_authenticated_user_id()
    if usuario_id is None:
        return jsonify({"error": NO_AUTENTICADO}), 401

    try:
        notificaciones = build_notificacion_service().list_notifications(usuario_id)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify([serialize_notificacion(n) for n in notificaciones]), 200


@notificacion_bp.get("/no-leidas")
def count_no_leidas():
    usuario_id = get_authenticated_user_id()
    if usuario_id is None:
        return jsonify({"error": NO_AUTENTICADO}), 401

    try:
        cantidad = build_notificacion_service().count_unread(usuario_id)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify({"cantidad": cantidad}), 200


@notificacion_bp.put("/<int:notificacion_id>/leer")
def marcar_leida(notificacion_id):
    usuario_id = get_authenticated_user_id()
    if usuario_id is None:
        return jsonify({"error": NO_AUTENTICADO}), 401

    try:
        build_notificacion_service().mark_as_read(usuario_id, notificacion_id)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify({"mensaje": "Notificación marcada como leída"}), 200


@notificacion_bp.put("/leer-todas")
def marcar_todas_leidas():
    usuario_id = get_authenticated_user_id()
    if usuario_id is None:
        return jsonify({"error": NO_AUTENTICADO}), 401

    try:
        build_notificacion_service().mark_all_as_read(usuario_id)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify({"mensaje": "Todas las notificaciones marcadas como leídas"}), 200
