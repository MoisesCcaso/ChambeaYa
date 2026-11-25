from flask import Blueprint, jsonify, request, session

from bootstrap.dependencies import container
from shared.http_messages import NOT_AUTHENTICATED


profile_bp = Blueprint("perfil", __name__, url_prefix="/perfil")


def build_intern_service():
    return container.get_intern_service()


def build_company_service():
    return container.get_company_service()


def serialize_intern(intern):
    return {
        "id": intern.id,
        "usuario_id": intern.user_id,
        "nombres": intern.first_names,
        "apellidos": intern.last_names,
        "dni": intern.dni,
        "carnet_universitario": intern.university_id_card,
        "habilidades": intern.skills,
        "formacion_educativa": intern.education,
        "score_reputacion": intern.reputation_score,
        "identidad_verificada": intern.identity_verified,
    }


def serialize_company(company):
    return {
        "id": company.id,
        "usuario_id": company.user_id,
        "razon_social": company.legal_name,
        "ruc": company.ruc.number if company.ruc else None,
        "verificada": company.verified,
    }


def get_authenticated_user_id():
    return session.get("usuario_id")


@profile_bp.get("/me")
def get_my_profile():
    user_id = get_authenticated_user_id()
    if user_id is None:
        return jsonify({"error": NOT_AUTHENTICATED}), 401

    user = container.get_user_repository().find_by_id(user_id)
    if user is None:
        return jsonify({"error": "Usuario no encontrado"}), 404
    if user.role == "empresa":
        profile = build_company_service().get_company_profile(user_id)
        serialize = serialize_company
    else:
        profile = build_intern_service().get_intern_profile(user_id)
        serialize = serialize_intern

    if profile is None:
        profile_type = "empresa" if user.role == "empresa" else "practicante"
        return jsonify({"error": f"Perfil de {profile_type} no encontrado"}), 404

    return jsonify(serialize(profile)), 200


@profile_bp.put("/me")
def update_my_profile():
    user_id = get_authenticated_user_id()
    if user_id is None:
        return jsonify({"error": NOT_AUTHENTICATED}), 401

    payload = request.get_json(silent=True) or {}
    data = serialize_intern(build_intern_service().update_intern(user_id, payload))

    return jsonify(data), 200

@profile_bp.put("/me/empresa")
def update_my_company():
    user_id = get_authenticated_user_id()
    if user_id is None:
        return jsonify({"error": NOT_AUTHENTICATED}), 401

    payload = request.get_json(silent=True) or {}
    data = serialize_company(build_company_service().update_company(user_id, payload))

    return jsonify(data), 200

@profile_bp.post("/me/habilidades")
def add_my_skill():
    user_id = get_authenticated_user_id()
    if user_id is None:
        return jsonify({"error": NOT_AUTHENTICATED}), 401

    payload = request.get_json(silent=True) or {}
    intern = build_intern_service().add_skill(user_id, payload.get("habilidad"))
    data = serialize_intern(intern)

    return jsonify(data), 200


@profile_bp.post("/me/formacion")
def add_my_education():
    user_id = get_authenticated_user_id()
    if user_id is None:
        return jsonify({"error": NOT_AUTHENTICATED}), 401

    payload = request.get_json(silent=True) or {}
    intern = build_intern_service().add_education(user_id, payload.get("formacion"))
    data = serialize_intern(intern)

    return jsonify(data), 200


@profile_bp.post("/me/identidad")
def verify_my_identity():
    user_id = get_authenticated_user_id()
    if user_id is None:
        return jsonify({"error": NOT_AUTHENTICATED}), 401

    payload = request.get_json(silent=True) or {}
    intern = build_intern_service().register_identity(
        user_id,
        dni=payload.get("dni"),
        university_id_card=payload.get("carnet_universitario"),
    )
    data = serialize_intern(intern)

    return jsonify(data), 200


@profile_bp.get("/me/reputacion")
def get_my_reputation():
    user_id = get_authenticated_user_id()
    if user_id is None:
        return jsonify({"error": NOT_AUTHENTICATED}), 401

    data = {"score_reputacion": build_intern_service().get_reputation_score(user_id)}

    return jsonify(data), 200
