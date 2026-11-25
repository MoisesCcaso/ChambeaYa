from flask import Blueprint, jsonify, request, session

from bootstrap.dependencies import container
from shared.http_messages import NOT_AUTHENTICATED


perfil_bp = Blueprint("perfil", __name__, url_prefix="/perfil")


def build_practicante_service():
    return container.get_practicante_service()


def build_empresa_service():
    return container.get_empresa_service()


def serialize_practicante(practicante):
    return {
        "id": practicante.id,
        "usuario_id": practicante.user_id,
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
        "usuario_id": empresa.user_id,
        "razon_social": empresa.razon_social,
        "ruc": empresa.ruc.numero if empresa.ruc else None,
        "verificada": empresa.verificada,
    }


def get_authenticated_user_id():
    return session.get("usuario_id")


@perfil_bp.get("/me")
def get_my_profile():
    user_id = get_authenticated_user_id()
    if user_id is None:
        return jsonify({"error": NOT_AUTHENTICATED}), 401

    user = container.get_user_repository().find_by_id(user_id)
    if user is None:
        return jsonify({"error": "Usuario no encontrado"}), 404
    if user.role == "empresa":
        perfil = build_empresa_service().get_empresa_profile(user_id)
        serialize = serialize_empresa
    else:
        perfil = build_practicante_service().get_practicante_profile(user_id)
        serialize = serialize_practicante

    if perfil is None:
        profile_type = "empresa" if user.role == "empresa" else "practicante"
        return jsonify({"error": f"Perfil de {profile_type} no encontrado"}), 404

    return jsonify(serialize(perfil)), 200


@perfil_bp.put("/me")
def update_my_profile():
    user_id = get_authenticated_user_id()
    if user_id is None:
        return jsonify({"error": NOT_AUTHENTICATED}), 401

    payload = request.get_json(silent=True) or {}
    data = serialize_practicante(build_practicante_service().update_practicante(user_id, payload))

    return jsonify(data), 200

@perfil_bp.put("/me/empresa")
def update_my_company():
    user_id = get_authenticated_user_id()
    if user_id is None:
        return jsonify({"error": NOT_AUTHENTICATED}), 401

    payload = request.get_json(silent=True) or {}
    data = serialize_empresa(build_empresa_service().update_empresa(user_id, payload))

    return jsonify(data), 200

@perfil_bp.post("/me/habilidades")
def add_my_skill():
    user_id = get_authenticated_user_id()
    if user_id is None:
        return jsonify({"error": NOT_AUTHENTICATED}), 401

    payload = request.get_json(silent=True) or {}
    practicante = build_practicante_service().add_habilidad(user_id, payload.get("habilidad"))
    data = serialize_practicante(practicante)

    return jsonify(data), 200


@perfil_bp.post("/me/formacion")
def add_my_education():
    user_id = get_authenticated_user_id()
    if user_id is None:
        return jsonify({"error": NOT_AUTHENTICATED}), 401

    payload = request.get_json(silent=True) or {}
    practicante = build_practicante_service().add_formacion(user_id, payload.get("formacion"))
    data = serialize_practicante(practicante)

    return jsonify(data), 200


@perfil_bp.post("/me/identidad")
def verify_my_identity():
    user_id = get_authenticated_user_id()
    if user_id is None:
        return jsonify({"error": NOT_AUTHENTICATED}), 401

    payload = request.get_json(silent=True) or {}
    practicante = build_practicante_service().register_identity(
        user_id,
        dni=payload.get("dni"),
        carnet_universitario=payload.get("carnet_universitario"),
    )
    data = serialize_practicante(practicante)

    return jsonify(data), 200


@perfil_bp.get("/me/reputacion")
def get_my_reputation():
    user_id = get_authenticated_user_id()
    if user_id is None:
        return jsonify({"error": NOT_AUTHENTICATED}), 401

    data = {"score_reputacion": build_practicante_service().get_reputation_score(user_id)}

    return jsonify(data), 200
