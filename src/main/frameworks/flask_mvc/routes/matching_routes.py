from flask import Blueprint, current_app, jsonify, session

from application.matching_application_service import MatchingApplicationService
from application.notificacion_application_service import NotificacionApplicationService
from domain.matching.matching_dominio_servicio import MatchingDominioServicio
from infrastructure.sqlalchemy_matching_repository import SqlAlchemyMatchingRepository
from infrastructure.sqlalchemy_notificacion_repository import SqlAlchemyNotificacionRepository
from infrastructure.sqlalchemy_perfil_repository import SqlAlchemyPerfilRepository
from infrastructure.sqlalchemy_convocatoria_repository import SqlAlchemyConvocatoriaRepository


matching_bp = Blueprint("matching", __name__, url_prefix="/matching")


def build_matching_service():
    sug_repo = SqlAlchemyMatchingRepository()
    per_repo = SqlAlchemyPerfilRepository()
    conv_repo = SqlAlchemyConvocatoriaRepository()
    servicio = MatchingDominioServicio()
    return MatchingApplicationService(sug_repo, per_repo, conv_repo, servicio)


def serialize_resultado(resultado):
    return {
        "practicante_id": resultado.practicante_id,
        "convocatoria_id": resultado.convocatoria_id,
        "score_compatibilidad": round(resultado.score_compatibilidad, 2),
        "es_compatible": resultado.es_compatible(),
        "habilidades_coincidentes": resultado.sugerencia.habilidades_coincidentes,
        "convocatoria": {
            "id": resultado.convocatoria.id,
            "titulo": resultado.convocatoria.titulo,
            "descripcion": resultado.convocatoria.descripcion,
            "beneficios": resultado.convocatoria.beneficios,
        } if resultado.convocatoria else None,
    }


@matching_bp.get("/sugerencias")
def suggest_convocatorias():
    """GET /matching/sugerencias — Obtener convocatorias sugeridas para el practicante."""
    usuario_id = session.get("usuario_id")

    if usuario_id is None:
        return jsonify({"error": "No autenticado"}), 401

    try:
        resultados = build_matching_service().suggest_convocatorias(usuario_id)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify([serialize_resultado(r) for r in resultados]), 200


@matching_bp.post("/calcular")
def calculate_match():
    """POST /matching/calcular — Calcular y guardar matching para el practicante."""
    usuario_id = session.get("usuario_id")

    if usuario_id is None:
        return jsonify({"error": "No autenticado"}), 401

    try:
        resultados = build_matching_service().calculate_for_practicante(usuario_id)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    data = [serialize_resultado(r) for r in resultados]

    if data:
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

    return jsonify(data), 200
