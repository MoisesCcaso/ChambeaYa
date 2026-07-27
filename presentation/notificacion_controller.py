# presentation/notificacion_controller.py
from flask import Blueprint, request, jsonify, session
from application.notificacion_application_service import NotificacionApplicationService
from infrastructure.sqlalchemy_notificacion_repository import SQLAlchemyNotificacionRepository
from frameworks.sqlalchemy_orm.database import db

notificacion_blueprint = Blueprint('notificacion', __name__, url_prefix='/notificaciones')

# Inicializar dependencias
notificacion_repo = SQLAlchemyNotificacionRepository(db.session)
notificacion_service = NotificacionApplicationService(notificacion_repo)


@notificacion_blueprint.route('', methods=['GET'])
def obtener_notificaciones():
    """Obtiene las notificaciones del usuario autenticado."""
    try:
        usuario_id = session.get('usuario_id')
        if not usuario_id:
            return jsonify({"error": "No autenticado"}), 401

        limit = request.args.get('limit', 50, type=int)
        if limit > 100:
            limit = 100

        notificaciones = notificacion_service.obtener_notificaciones(usuario_id, limit)
        return jsonify({
            "data": notificaciones,
            "total": len(notificaciones)
        }), 200

    except Exception as e:
        return jsonify({"error": f"Error interno: {str(e)}"}), 500


@notificacion_blueprint.route('/no-leidas', methods=['GET'])
def obtener_no_leidas():
    """Obtiene las notificaciones no leídas del usuario autenticado."""
    try:
        usuario_id = session.get('usuario_id')
        if not usuario_id:
            return jsonify({"error": "No autenticado"}), 401

        notificaciones = notificacion_service.obtener_no_leidas(usuario_id)
        return jsonify({
            "data": notificaciones,
            "total": len(notificaciones)
        }), 200

    except Exception as e:
        return jsonify({"error": f"Error interno: {str(e)}"}), 500


@notificacion_blueprint.route('/<int:notificacion_id>/leer', methods=['PATCH'])
def marcar_como_leida(notificacion_id):
    """Marca una notificación como leída."""
    try:
        usuario_id = session.get('usuario_id')
        if not usuario_id:
            return jsonify({"error": "No autenticado"}), 401

        notificacion = notificacion_service.marcar_como_leida(notificacion_id, usuario_id)
        return jsonify(notificacion), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except PermissionError as e:
        return jsonify({"error": str(e)}), 403
    except Exception as e:
        return jsonify({"error": f"Error interno: {str(e)}"}), 500


@notificacion_blueprint.route('/leer-todas', methods=['PATCH'])
def marcar_todas_como_leidas():
    """Marca todas las notificaciones del usuario como leídas."""
    try:
        usuario_id = session.get('usuario_id')
        if not usuario_id:
            return jsonify({"error": "No autenticado"}), 401

        count = notificacion_service.marcar_todas_como_leidas(usuario_id)
        return jsonify({
            "message": f"{count} notificaciones marcadas como leídas",
            "count": count
        }), 200

    except Exception as e:
        return jsonify({"error": f"Error interno: {str(e)}"}), 500