from flask import Blueprint, jsonify, request, session

from bootstrap.dependencies import container
from shared.http_messages import NOT_AUTHENTICATED, COMPANY_NOT_FOUND


convocatoria_bp = Blueprint("convocatoria", __name__, url_prefix="/convocatorias")


def build_convocatoria_service():
    return container.get_convocatoria_service()


def get_authenticated_company(user_id):
    if user_id is None:
        return None
    return container.get_profile_repository().find_company_by_user_id(user_id)


def serialize_convocatoria(convocatoria):
    return {
        "id": convocatoria.id,
        "empresa_id": convocatoria.company_id,
        "titulo": convocatoria.titulo,
        "descripcion": convocatoria.descripcion,
        "estado": convocatoria.status,
        "habilidades_requeridas": convocatoria.habilidades_requeridas,
        "beneficios": convocatoria.beneficios,
        "fecha_publicacion": (
            convocatoria.fecha_publicacion.isoformat()
            if convocatoria.fecha_publicacion
            else None
        ),
        "fecha_cierre": (
            convocatoria.fecha_cierre.isoformat()
            if convocatoria.fecha_cierre
            else None
        ),
    }


def get_authenticated_user_id():
    return session.get("usuario_id")


@convocatoria_bp.get("")
def list_convocatorias():
    convocatorias = build_convocatoria_service().search(request.args.get("q"), "publicada")
    return jsonify([serialize_convocatoria(item) for item in convocatorias]), 200


@convocatoria_bp.get("/mis")
def list_my_convocatorias():
    user_id = get_authenticated_user_id()
    if user_id is None:
        return jsonify({"error": NOT_AUTHENTICATED}), 401
    company = get_authenticated_company(user_id)
    if company is None:
        return jsonify({"error": COMPANY_NOT_FOUND}), 403
    convocatorias = build_convocatoria_service().list_for_empresa(company.id)
    return jsonify([serialize_convocatoria(item) for item in convocatorias]), 200


@convocatoria_bp.get("/<int:convocatoria_id>")
def get_convocatoria(convocatoria_id):
    data = serialize_convocatoria(build_convocatoria_service().find_by_id(convocatoria_id))
    if data["estado"] != "publicada":
        user_id = get_authenticated_user_id()
        company = get_authenticated_company(user_id)
        if company is None or company.id != data["empresa_id"]:
            return jsonify({"error": "Convocatoria no encontrada"}), 404
    return jsonify(data), 200


@convocatoria_bp.post("")
def create_convocatoria():
    user_id = get_authenticated_user_id()
    if user_id is None:
        return jsonify({"error": NOT_AUTHENTICATED}), 401

    company = get_authenticated_company(user_id)
    if company is None:
        return jsonify({"error": COMPANY_NOT_FOUND}), 403
    if not company.verified:
        return jsonify({"error": "La empresa debe estar verificada"}), 403

    payload = request.get_json(silent=True) or {}
    convocatoria = build_convocatoria_service().create_convocatoria(company.id, payload)

    return jsonify(serialize_convocatoria(convocatoria)), 201

@convocatoria_bp.post("/<int:convocatoria_id>/publicar")
def publish_convocatoria(convocatoria_id):
    user_id = get_authenticated_user_id()
    if user_id is None:
        return jsonify({"error": NOT_AUTHENTICATED}), 401

    company = get_authenticated_company(user_id)
    if company is None:
        return jsonify({"error": COMPANY_NOT_FOUND}), 403

    convocatoria = build_convocatoria_service().publish(company.id, convocatoria_id)

    return jsonify(serialize_convocatoria(convocatoria)), 200


@convocatoria_bp.put("/<int:convocatoria_id>")
def update_convocatoria(convocatoria_id):
    user_id = get_authenticated_user_id()
    if user_id is None:
        return jsonify({"error": NOT_AUTHENTICATED}), 401
    company = get_authenticated_company(user_id)
    if company is None:
        return jsonify({"error": COMPANY_NOT_FOUND}), 403
    convocatoria = build_convocatoria_service().update(
        company.id,
        convocatoria_id,
        request.get_json(silent=True) or {},
    )
    return jsonify(serialize_convocatoria(convocatoria)), 200


@convocatoria_bp.post("/<int:convocatoria_id>/cerrar")
def close_convocatoria(convocatoria_id):
    user_id = get_authenticated_user_id()
    if user_id is None:
        return jsonify({"error": NOT_AUTHENTICATED}), 401

    company = get_authenticated_company(user_id)
    if company is None:
        return jsonify({"error": COMPANY_NOT_FOUND}), 403

    convocatoria = build_convocatoria_service().close(company.id, convocatoria_id)
    return jsonify(serialize_convocatoria(convocatoria)), 200


@convocatoria_bp.post("/<int:convocatoria_id>/reabrir")
def reopen_convocatoria(convocatoria_id):
    user_id = get_authenticated_user_id()
    if user_id is None:
        return jsonify({"error": NOT_AUTHENTICATED}), 401
    company = get_authenticated_company(user_id)
    if company is None:
        return jsonify({"error": COMPANY_NOT_FOUND}), 403
    convocatoria = build_convocatoria_service().reopen(company.id, convocatoria_id)
    return jsonify(serialize_convocatoria(convocatoria)), 200


@convocatoria_bp.post("/<int:convocatoria_id>/duplicar")
def duplicate_convocatoria(convocatoria_id):
    user_id = get_authenticated_user_id()
    if user_id is None:
        return jsonify({"error": NOT_AUTHENTICATED}), 401
    company = get_authenticated_company(user_id)
    if company is None:
        return jsonify({"error": COMPANY_NOT_FOUND}), 403
    convocatoria = build_convocatoria_service().duplicate(company.id, convocatoria_id)
    return jsonify(serialize_convocatoria(convocatoria)), 201


@convocatoria_bp.delete("/<int:convocatoria_id>")
def delete_convocatoria(convocatoria_id):
    user_id = get_authenticated_user_id()
    if user_id is None:
        return jsonify({"error": NOT_AUTHENTICATED}), 401
    company = get_authenticated_company(user_id)
    if company is None:
        return jsonify({"error": COMPANY_NOT_FOUND}), 403
    convocatoria = build_convocatoria_service().delete(company.id, convocatoria_id)
    return jsonify({"id": convocatoria.id, "mensaje": "Convocatoria eliminada"}), 200
