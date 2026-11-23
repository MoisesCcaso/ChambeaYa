from flask import Blueprint, jsonify, request, session

from frameworks.flask_mvc.dependencies import container
from frameworks.flask_mvc.routes.mensajes import NO_AUTENTICADO


perfil_bp = Blueprint("perfil", __name__, url_prefix="/perfil")


def build_practicante_service():
    return container.get_practicante_service()


def build_empresa_service():
    return container.get_empresa_service()


def serialize_practicante(practicante):
    return {
        "id": practicante.id,
        "usuario_id": practicante.usuario_id,
        "nombres": practicante.nombres,
        "apellidos": practicante.apellidos,
        "dni": practicante.dni,
        "carnet_universitario": practicante.carnet_universitario,
        "habilidades": practicante.habilidades,
        "formacion_educativa": practicante.formacion_educativa,
        "score_reputacion": practicante.score_reputacion,
        "identidad_verificada": practicante.identidad_verificada,
    }


def serialize_empresa(empresa):
    return {
        "id": empresa.id,
        "usuario_id": empresa.usuario_id,
        "razon_social": empresa.razon_social,
        "ruc": empresa.ruc.numero if empresa.ruc else None,
        "verificada": empresa.verificada,
    }


def get_authenticated_user_id():
    return session.get("usuario_id")


@perfil_bp.get("/me")
def get_my_profile():
    usuario_id = get_authenticated_user_id()
    if usuario_id is None:
        return jsonify({"error": NO_AUTENTICADO}), 401

    try:
        usuario = container.get_usuario_repository().find_by_id(usuario_id)
        if usuario is None:
            return jsonify({"error": "Usuario no encontrado"}), 404
        if usuario.tipo == "empresa":
            perfil = build_empresa_service().get_empresa_profile(usuario_id)
            serialize = serialize_empresa
        else:
            perfil = build_practicante_service().get_practicante_profile(usuario_id)
            serialize = serialize_practicante
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    if perfil is None:
        profile_type = "empresa" if usuario.tipo == "empresa" else "practicante"
        return jsonify({"error": f"Perfil de {profile_type} no encontrado"}), 404

    return jsonify(serialize(perfil)), 200


@perfil_bp.put("/me")
def update_my_profile():
    usuario_id = get_authenticated_user_id()
    if usuario_id is None:
        return jsonify({"error": NO_AUTENTICADO}), 401

    payload = request.get_json(silent=True) or {}
    try:
        data = serialize_practicante(build_practicante_service().update_practicante(usuario_id, payload))
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify(data), 200

@perfil_bp.put("/me/empresa")
def update_my_company():
    usuario_id = get_authenticated_user_id()
    if usuario_id is None:
        return jsonify({"error": NO_AUTENTICADO}), 401

    payload = request.get_json(silent=True) or {}
    try:
        data = serialize_empresa(build_empresa_service().update_empresa(usuario_id, payload))
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify(data), 200

@perfil_bp.post("/me/habilidades")
def add_my_skill():
    usuario_id = get_authenticated_user_id()
    if usuario_id is None:
        return jsonify({"error": NO_AUTENTICADO}), 401

    payload = request.get_json(silent=True) or {}
    try:
        practicante = build_practicante_service().add_habilidad(usuario_id, payload.get("habilidad"))
        data = serialize_practicante(practicante)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify(data), 200


@perfil_bp.post("/me/formacion")
def add_my_education():
    usuario_id = get_authenticated_user_id()
    if usuario_id is None:
        return jsonify({"error": NO_AUTENTICADO}), 401

    payload = request.get_json(silent=True) or {}
    try:
        practicante = build_practicante_service().add_formacion(usuario_id, payload.get("formacion"))
        data = serialize_practicante(practicante)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify(data), 200


@perfil_bp.post("/me/identidad")
def verify_my_identity():
    usuario_id = get_authenticated_user_id()
    if usuario_id is None:
        return jsonify({"error": NO_AUTENTICADO}), 401

    payload = request.get_json(silent=True) or {}
    try:
        practicante = build_practicante_service().register_identity(
            usuario_id,
            dni=payload.get("dni"),
            carnet_universitario=payload.get("carnet_universitario"),
        )
        data = serialize_practicante(practicante)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify(data), 200


@perfil_bp.get("/me/reputacion")
def get_my_reputation():
    usuario_id = get_authenticated_user_id()
    if usuario_id is None:
        return jsonify({"error": NO_AUTENTICADO}), 401

    try:
        data = {"score_reputacion": build_practicante_service().get_reputation_score(usuario_id)}
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify(data), 200
