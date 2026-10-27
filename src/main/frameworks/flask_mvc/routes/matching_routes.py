from flask import Blueprint, current_app, jsonify, session

from application.matching_application_service import MatchingApplicationService
from application.notificacion_application_service import NotificacionApplicationService
from domain.matching.matching_dominio_servicio import MatchingDominioServicio
from infrastructure.sqlalchemy_matching_repository import SqlAlchemyMatchingRepository
from infrastructure.sqlalchemy_notificacion_repository import SqlAlchemyNotificacionRepository
from infrastructure.sqlalchemy_perfil_repository import SqlAlchemyPerfilRepository
from infrastructure.sqlalchemy_convocatoria_repository import SqlAlchemyConvocatoriaRepository
from presentation.matching_controller import MatchingController


matching_bp = Blueprint("matching", __name__, url_prefix="/matching")


def build_matching_controller():
    sug_repo = SqlAlchemyMatchingRepository()
    per_repo = SqlAlchemyPerfilRepository()
    conv_repo = SqlAlchemyConvocatoriaRepository()
    servicio = MatchingDominioServicio()
    app_service = MatchingApplicationService(sug_repo, per_repo, conv_repo, servicio)
    return MatchingController(app_service)


@matching_bp.get("/sugerencias")
def suggest_convocatorias():
    """GET /matching/sugerencias — Obtener convocatorias sugeridas para el practicante."""
    usuario_id = session.get("usuario_id")

    if usuario_id is None:
        return jsonify({"error": "No autenticado"}), 401

    controller = build_matching_controller()

    try:
        data, status_code = controller.suggest_convocatorias(usuario_id)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify(data), status_code


@matching_bp.post("/calcular")
def calculate_match():
    """POST /matching/calcular — Calcular y guardar matching para el practicante."""
    usuario_id = session.get("usuario_id")

    if usuario_id is None:
        return jsonify({"error": "No autenticado"}), 401

    controller = build_matching_controller()

    try:
        data, status_code = controller.calculate_match(usuario_id)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    if status_code == 200 and data:
        try:
            repo = SqlAlchemyNotificacionRepository()
            notif_service = NotificacionApplicationService(writer=repo, reader=repo)
            notif_service.create_notification(
                usuario_destino_id=usuario_id,
                tipo="NUEVAS_SUGERENCIAS",
                mensaje="Nuevas sugerencias de convocatorias disponibles",
            )
        except Exception:
            current_app.logger.exception(
                "No se pudo crear la notificación de nuevas sugerencias"
            )

    return jsonify(data), status_code
