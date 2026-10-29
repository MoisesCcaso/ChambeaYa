from flask import Blueprint, jsonify, request, session

from application.convocatoria_application_service import ConvocatoriaApplicationService
from infrastructure.sqlalchemy_convocatoria_repository import SqlAlchemyConvocatoriaRepository
from infrastructure.sqlalchemy_perfil_repository import SqlAlchemyPerfilRepository
from presentation.convocatoria_controller import ConvocatoriaController


convocatoria_bp = Blueprint("convocatoria", __name__, url_prefix="/convocatorias")


def build_convocatoria_controller():
    convocatoria_repository = SqlAlchemyConvocatoriaRepository()
    service = ConvocatoriaApplicationService(convocatoria_repository)
    return ConvocatoriaController(service)


def get_authenticated_user_id():
    return session.get("usuario_id")


@convocatoria_bp.get("")
def list_convocatorias():
    controller = build_convocatoria_controller()
    data, status_code = controller.list(
        query=request.args.get("q"),
        estado="publicada",
    )
    return jsonify(data), status_code


@convocatoria_bp.get("/mis")
def list_my_convocatorias():
    usuario_id = get_authenticated_user_id()
    if usuario_id is None:
        return jsonify({"error": "No autenticado"}), 401
    empresa = SqlAlchemyPerfilRepository().find_empresa_by_user_id(usuario_id)
    if empresa is None:
        return jsonify({"error": "Empresa no encontrada para este usuario"}), 400
    data, status_code = build_convocatoria_controller().list_for_empresa(empresa.id)
    return jsonify(data), status_code


@convocatoria_bp.get("/<int:convocatoria_id>")
def get_convocatoria(convocatoria_id):
    controller = build_convocatoria_controller()
    try:
        data, status_code = controller.get(convocatoria_id)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 404
    if data["estado"] != "publicada":
        usuario_id = get_authenticated_user_id()
        empresa = (
            SqlAlchemyPerfilRepository().find_empresa_by_user_id(usuario_id)
            if usuario_id is not None
            else None
        )
        if empresa is None or empresa.id != data["empresa_id"]:
            return jsonify({"error": "Convocatoria no encontrada"}), 404
    return jsonify(data), status_code


@convocatoria_bp.post("")
def create_convocatoria():
    usuario_id = get_authenticated_user_id()
    if usuario_id is None:
        return jsonify({"error": "No autenticado"}), 401

    perfil_repository = SqlAlchemyPerfilRepository()
    empresa = perfil_repository.find_empresa_by_user_id(usuario_id)
    if empresa is None:
        return jsonify({"error": "Empresa no encontrada para este usuario"}), 400
    if not empresa.verificada:
        return jsonify({"error": "La empresa debe estar verificada"}), 400

    payload = request.get_json(silent=True) or {}
    controller = build_convocatoria_controller()
    try:
        data, status_code = controller.create(empresa.id, payload)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify(data), status_code

@convocatoria_bp.post("/<int:convocatoria_id>/publicar")
def publish_convocatoria(convocatoria_id):
    usuario_id = get_authenticated_user_id()
    if usuario_id is None:
        return jsonify({"error": "No autenticado"}), 401

    perfil_repository = SqlAlchemyPerfilRepository()
    empresa = perfil_repository.find_empresa_by_user_id(usuario_id)
    if empresa is None:
        return jsonify({"error": "Empresa no encontrada para este usuario"}), 400

    controller = build_convocatoria_controller()
    try:
        data, status_code = controller.publish(empresa.id, convocatoria_id)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify(data), status_code


@convocatoria_bp.put("/<int:convocatoria_id>")
def update_convocatoria(convocatoria_id):
    usuario_id = get_authenticated_user_id()
    if usuario_id is None:
        return jsonify({"error": "No autenticado"}), 401
    empresa = SqlAlchemyPerfilRepository().find_empresa_by_user_id(usuario_id)
    if empresa is None:
        return jsonify({"error": "Empresa no encontrada para este usuario"}), 400
    try:
        data, status_code = build_convocatoria_controller().update(
            empresa.id,
            convocatoria_id,
            request.get_json(silent=True) or {},
        )
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    return jsonify(data), status_code


@convocatoria_bp.post("/<int:convocatoria_id>/cerrar")
def close_convocatoria(convocatoria_id):
    usuario_id = get_authenticated_user_id()
    if usuario_id is None:
        return jsonify({"error": "No autenticado"}), 401

    empresa = SqlAlchemyPerfilRepository().find_empresa_by_user_id(usuario_id)
    if empresa is None:
        return jsonify({"error": "Empresa no encontrada para este usuario"}), 400

    try:
        data, status_code = build_convocatoria_controller().close(
            empresa.id, convocatoria_id
        )
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    return jsonify(data), status_code


@convocatoria_bp.post("/<int:convocatoria_id>/reabrir")
def reopen_convocatoria(convocatoria_id):
    usuario_id = get_authenticated_user_id()
    if usuario_id is None:
        return jsonify({"error": "No autenticado"}), 401
    empresa = SqlAlchemyPerfilRepository().find_empresa_by_user_id(usuario_id)
    if empresa is None:
        return jsonify({"error": "Empresa no encontrada para este usuario"}), 400
    try:
        data, status_code = build_convocatoria_controller().reopen(
            empresa.id, convocatoria_id
        )
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    return jsonify(data), status_code


@convocatoria_bp.post("/<int:convocatoria_id>/duplicar")
def duplicate_convocatoria(convocatoria_id):
    usuario_id = get_authenticated_user_id()
    if usuario_id is None:
        return jsonify({"error": "No autenticado"}), 401
    empresa = SqlAlchemyPerfilRepository().find_empresa_by_user_id(usuario_id)
    if empresa is None:
        return jsonify({"error": "Empresa no encontrada para este usuario"}), 400
    try:
        data, status_code = build_convocatoria_controller().duplicate(
            empresa.id, convocatoria_id
        )
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    return jsonify(data), status_code


@convocatoria_bp.delete("/<int:convocatoria_id>")
def delete_convocatoria(convocatoria_id):
    usuario_id = get_authenticated_user_id()
    if usuario_id is None:
        return jsonify({"error": "No autenticado"}), 401
    empresa = SqlAlchemyPerfilRepository().find_empresa_by_user_id(usuario_id)
    if empresa is None:
        return jsonify({"error": "Empresa no encontrada para este usuario"}), 400
    try:
        data, status_code = build_convocatoria_controller().delete(
            empresa.id, convocatoria_id
        )
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    return jsonify(data), status_code
