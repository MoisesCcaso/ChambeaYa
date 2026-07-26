from flask import Blueprint, jsonify, session

from application.notificacion_application_service import NotificacionApplicationService
from infrastructure.sqlalchemy_notificacion_repository import SqlAlchemyNotificacionRepository
from presentation.notificacion_controller import NotificacionController


notificacion_bp = Blueprint("notificacion", __name__, url_prefix="/notificaciones")


def build_notificacion_controller():
    repo = SqlAlchemyNotificacionRepository()
    service = NotificacionApplicationService(writer=repo, reader=repo)
    return NotificacionController(service)


def get_authenticated_user_id():
    return session.get("usuario_id")


@notificacion_bp.get("")
def list_notificaciones():
    usuario_id = get_authenticated_user_id()
    if usuario_id is None:
        return jsonify({"error": "No autenticado"}), 401

    controller = build_notificacion_controller()
    try:
        data, status_code = controller.list_notifications(usuario_id)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify(data), status_code


@notificacion_bp.get("/no-leidas")
def count_no_leidas():
    usuario_id = get_authenticated_user_id()
    if usuario_id is None:
        return jsonify({"error": "No autenticado"}), 401

    controller = build_notificacion_controller()
    try:
        data, status_code = controller.count_unread(usuario_id)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify(data), status_code


@notificacion_bp.put("/<int:notificacion_id>/leer")
def marcar_leida(notificacion_id):
    usuario_id = get_authenticated_user_id()
    if usuario_id is None:
        return jsonify({"error": "No autenticado"}), 401

    controller = build_notificacion_controller()
    try:
        data, status_code = controller.mark_as_read(notificacion_id)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify(data), status_code


@notificacion_bp.put("/leer-todas")
def marcar_todas_leidas():
    usuario_id = get_authenticated_user_id()
    if usuario_id is None:
        return jsonify({"error": "No autenticado"}), 401

    controller = build_notificacion_controller()
    try:
        data, status_code = controller.mark_all_as_read(usuario_id)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify(data), status_code
