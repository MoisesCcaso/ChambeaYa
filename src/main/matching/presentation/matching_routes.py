from flask import Blueprint, current_app, jsonify, session

from bootstrap.dependencies import container
from shared.http_messages import NOT_AUTHENTICATED


matching_bp = Blueprint("matching", __name__, url_prefix="/matching")


def build_matching_service():
    return container.get_matching_service()


def serialize_resultado(result):
    return {
        "practicante_id": result.intern_id,
        "convocatoria_id": result.job_posting_id,
        "score_compatibilidad": round(result.score_compatibilidad, 2),
        "es_compatible": result.es_compatible(),
        "habilidades_coincidentes": result.sugerencia.habilidades_coincidentes,
        "convocatoria": {
            "id": result.job_posting.id,
            "titulo": result.job_posting.title,
            "descripcion": result.job_posting.description,
            "beneficios": result.job_posting.benefits,
        } if result.job_posting else None,
    }


@matching_bp.get("/sugerencias")
def suggest_convocatorias():
    """GET /matching/sugerencias — Obtener convocatorias sugeridas para el practicante."""
    user_id = session.get("usuario_id")

    if user_id is None:
        return jsonify({"error": NOT_AUTHENTICATED}), 401

    results = build_matching_service().suggest_convocatorias(user_id)

    return jsonify([serialize_resultado(r) for r in results]), 200


@matching_bp.post("/calcular")
def calculate_match():
    """POST /matching/calcular — Calcular y guardar matching para el practicante."""
    user_id = session.get("usuario_id")

    if user_id is None:
        return jsonify({"error": NOT_AUTHENTICATED}), 401

    results = build_matching_service().calculate_for_practicante(user_id)
    data = [serialize_resultado(r) for r in results]

    if data:
        try:
            notif_service = container.get_notification_service()
            notif_service.create_notification(
                recipient_user_id=user_id,
                notification_type="NUEVAS_SUGERENCIAS",
                message="Nuevas sugerencias de convocatorias disponibles",
            )
        except Exception:
            current_app.logger.exception(
                "No se pudo crear la notificación de nuevas sugerencias"
            )

    return jsonify(data), 200
