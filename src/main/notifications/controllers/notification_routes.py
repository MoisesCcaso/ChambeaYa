from flask import Blueprint, jsonify, session

from bootstrap.dependencies import container
from shared.http_messages import NOT_AUTHENTICATED


# Blueprint name, URLs and JSON keys are the public API contract: they stay in Spanish.
notification_bp = Blueprint("notificacion", __name__, url_prefix="/notificaciones")


def build_notification_service():
    return container.get_notification_service()


def serialize_notification(notification):
    return {
        "id": notification.id,
        "usuario_destino_id": notification.recipient_user_id,
        "tipo": notification.notification_type,
        "mensaje": notification.message,
        "metadata": notification.metadata,
        "leida": notification.is_read,
        "created_at": notification.created_at.isoformat() if notification.created_at else None,
    }


def get_authenticated_user_id():
    return session.get("usuario_id")


@notification_bp.get("")
def list_notifications():
    user_id = get_authenticated_user_id()
    if user_id is None:
        return jsonify({"error": NOT_AUTHENTICATED}), 401

    notifications = build_notification_service().list_notifications(user_id)

    return jsonify([serialize_notification(n) for n in notifications]), 200


@notification_bp.get("/no-leidas")
def count_unread():
    user_id = get_authenticated_user_id()
    if user_id is None:
        return jsonify({"error": NOT_AUTHENTICATED}), 401

    count = build_notification_service().count_unread(user_id)

    return jsonify({"cantidad": count}), 200


@notification_bp.put("/<int:notification_id>/leer")
def mark_as_read(notification_id):
    user_id = get_authenticated_user_id()
    if user_id is None:
        return jsonify({"error": NOT_AUTHENTICATED}), 401

    build_notification_service().mark_as_read(user_id, notification_id)

    return jsonify({"mensaje": "Notificación marcada como leída"}), 200


@notification_bp.put("/leer-todas")
def mark_all_as_read():
    user_id = get_authenticated_user_id()
    if user_id is None:
        return jsonify({"error": NOT_AUTHENTICATED}), 401

    build_notification_service().mark_all_as_read(user_id)

    return jsonify({"mensaje": "Todas las notificaciones marcadas como leídas"}), 200
