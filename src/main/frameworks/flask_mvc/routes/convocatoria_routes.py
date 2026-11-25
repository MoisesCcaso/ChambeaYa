from flask import Blueprint, jsonify, request, session

from bootstrap.dependencies import container
from shared.http_messages import NOT_AUTHENTICATED, COMPANY_NOT_FOUND


convocatoria_bp = Blueprint("convocatoria", __name__, url_prefix="/convocatorias")


def build_convocatoria_service():
    return container.get_convocatoria_service()


def get_authenticated_empresa(usuario_id):
    if usuario_id is None:
        return None
    return container.get_perfil_repository().find_empresa_by_user_id(usuario_id)


def serialize_convocatoria(convocatoria):
    return {
        "id": convocatoria.id,
        "empresa_id": convocatoria.empresa_id,
        "titulo": convocatoria.titulo,
        "descripcion": convocatoria.descripcion,
        "estado": convocatoria.estado,
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
    usuario_id = get_authenticated_user_id()
    if usuario_id is None:
        return jsonify({"error": NOT_AUTHENTICATED}), 401
    empresa = get_authenticated_empresa(usuario_id)
    if empresa is None:
        return jsonify({"error": COMPANY_NOT_FOUND}), 403
    convocatorias = build_convocatoria_service().list_for_empresa(empresa.id)
    return jsonify([serialize_convocatoria(item) for item in convocatorias]), 200


@convocatoria_bp.get("/<int:convocatoria_id>")
def get_convocatoria(convocatoria_id):
    data = serialize_convocatoria(build_convocatoria_service().find_by_id(convocatoria_id))
    if data["estado"] != "publicada":
        usuario_id = get_authenticated_user_id()
        empresa = get_authenticated_empresa(usuario_id)
        if empresa is None or empresa.id != data["empresa_id"]:
            return jsonify({"error": "Convocatoria no encontrada"}), 404
    return jsonify(data), 200


@convocatoria_bp.post("")
def create_convocatoria():
    usuario_id = get_authenticated_user_id()
    if usuario_id is None:
        return jsonify({"error": NOT_AUTHENTICATED}), 401

    empresa = get_authenticated_empresa(usuario_id)
    if empresa is None:
        return jsonify({"error": COMPANY_NOT_FOUND}), 403
    if not empresa.verificada:
        return jsonify({"error": "La empresa debe estar verificada"}), 403

    payload = request.get_json(silent=True) or {}
    convocatoria = build_convocatoria_service().create_convocatoria(empresa.id, payload)

    return jsonify(serialize_convocatoria(convocatoria)), 201

@convocatoria_bp.post("/<int:convocatoria_id>/publicar")
def publish_convocatoria(convocatoria_id):
    usuario_id = get_authenticated_user_id()
    if usuario_id is None:
        return jsonify({"error": NOT_AUTHENTICATED}), 401

    empresa = get_authenticated_empresa(usuario_id)
    if empresa is None:
        return jsonify({"error": COMPANY_NOT_FOUND}), 403

    convocatoria = build_convocatoria_service().publish(empresa.id, convocatoria_id)

    return jsonify(serialize_convocatoria(convocatoria)), 200


@convocatoria_bp.put("/<int:convocatoria_id>")
def update_convocatoria(convocatoria_id):
    usuario_id = get_authenticated_user_id()
    if usuario_id is None:
        return jsonify({"error": NOT_AUTHENTICATED}), 401
    empresa = get_authenticated_empresa(usuario_id)
    if empresa is None:
        return jsonify({"error": COMPANY_NOT_FOUND}), 403
    convocatoria = build_convocatoria_service().update(
        empresa.id,
        convocatoria_id,
        request.get_json(silent=True) or {},
    )
    return jsonify(serialize_convocatoria(convocatoria)), 200


@convocatoria_bp.post("/<int:convocatoria_id>/cerrar")
def close_convocatoria(convocatoria_id):
    usuario_id = get_authenticated_user_id()
    if usuario_id is None:
        return jsonify({"error": NOT_AUTHENTICATED}), 401

    empresa = get_authenticated_empresa(usuario_id)
    if empresa is None:
        return jsonify({"error": COMPANY_NOT_FOUND}), 403

    convocatoria = build_convocatoria_service().close(empresa.id, convocatoria_id)
    return jsonify(serialize_convocatoria(convocatoria)), 200


@convocatoria_bp.post("/<int:convocatoria_id>/reabrir")
def reopen_convocatoria(convocatoria_id):
    usuario_id = get_authenticated_user_id()
    if usuario_id is None:
        return jsonify({"error": NOT_AUTHENTICATED}), 401
    empresa = get_authenticated_empresa(usuario_id)
    if empresa is None:
        return jsonify({"error": COMPANY_NOT_FOUND}), 403
    convocatoria = build_convocatoria_service().reopen(empresa.id, convocatoria_id)
    return jsonify(serialize_convocatoria(convocatoria)), 200


@convocatoria_bp.post("/<int:convocatoria_id>/duplicar")
def duplicate_convocatoria(convocatoria_id):
    usuario_id = get_authenticated_user_id()
    if usuario_id is None:
        return jsonify({"error": NOT_AUTHENTICATED}), 401
    empresa = get_authenticated_empresa(usuario_id)
    if empresa is None:
        return jsonify({"error": COMPANY_NOT_FOUND}), 403
    convocatoria = build_convocatoria_service().duplicate(empresa.id, convocatoria_id)
    return jsonify(serialize_convocatoria(convocatoria)), 201


@convocatoria_bp.delete("/<int:convocatoria_id>")
def delete_convocatoria(convocatoria_id):
    usuario_id = get_authenticated_user_id()
    if usuario_id is None:
        return jsonify({"error": NOT_AUTHENTICATED}), 401
    empresa = get_authenticated_empresa(usuario_id)
    if empresa is None:
        return jsonify({"error": COMPANY_NOT_FOUND}), 403
    convocatoria = build_convocatoria_service().delete(empresa.id, convocatoria_id)
    return jsonify({"id": convocatoria.id, "mensaje": "Convocatoria eliminada"}), 200
