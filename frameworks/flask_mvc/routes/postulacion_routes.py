from flask import Blueprint, jsonify, session

from application.notificacion_application_service import NotificacionApplicationService
from application.postulacion_application_service import PostulacionApplicationService
from infrastructure.sqlalchemy_notificacion_repository import SqlAlchemyNotificacionRepository
from infrastructure.sqlalchemy_postulacion_repository import SqlAlchemyPostulacionRepository
from infrastructure.sqlalchemy_convocatoria_repository import SqlAlchemyConvocatoriaRepository
from infrastructure.sqlalchemy_perfil_repository import SqlAlchemyPerfilRepository
from presentation.notificacion_controller import NotificacionController
from presentation.postulacion_controller import PostulacionController


postulacion_bp = Blueprint("postulacion", __name__, url_prefix="/postulaciones")


def build_postulacion_controller():
    postulacion_repository = SqlAlchemyPostulacionRepository()
    convocatoria_repository = SqlAlchemyConvocatoriaRepository()
    service = PostulacionApplicationService(postulacion_repository, convocatoria_repository)
    return PostulacionController(service)


def get_authenticated_user_id():
    return session.get("usuario_id")


@postulacion_bp.post("/<int:postulacion_id>/seleccionar")
def select_postulacion(postulacion_id):
    usuario_id = get_authenticated_user_id()
    if usuario_id is None:
        return jsonify({"error": "No autenticado"}), 401

    perfil_repository = SqlAlchemyPerfilRepository()
    empresa = perfil_repository.find_empresa_by_user_id(usuario_id)
    if empresa is None:
        return jsonify({"error": "Empresa no encontrada para este usuario"}), 400

    controller = build_postulacion_controller()
    try:
        data, status_code = controller.select(empresa.id, postulacion_id)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    if status_code == 200:
        try:
            repo = SqlAlchemyNotificacionRepository()
            notif_service = NotificacionApplicationService(writer=repo, reader=repo)
            perfil_repo = SqlAlchemyPerfilRepository()
            practicante = perfil_repo.find_practicante_by_id(data["practicante_id"])
            if practicante:
                notif_service.create_notification(
                    usuario_destino_id=practicante.usuario_id,
                    tipo="POSTULACION_SELECCIONADA",
                    mensaje="Has sido seleccionado para una convocatoria",
                    metadata={"postulacion_id": postulacion_id},
                )
        except Exception:
            pass

    return jsonify(data), status_code