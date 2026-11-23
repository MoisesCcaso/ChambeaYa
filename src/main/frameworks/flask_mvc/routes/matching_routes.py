from flask import Blueprint, current_app, jsonify, session

from frameworks.flask_mvc.dependencies import container


matching_bp = Blueprint("matching", __name__, url_prefix="/matching")


def build_matching_service():
    return container.get_matching_service()


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
            notif_service = container.get_notificacion_service()
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
