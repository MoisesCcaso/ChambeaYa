# presentation/matching_controller.py
# LAB 12 - SOLID: S (Responsabilidad Única)
# El controlador SOLO maneja peticiones HTTP. No contiene lógica de negocio.

from flask import Blueprint, request, jsonify, session
from application.matching_application_service import MatchingApplicationService
from infrastructure.sqlalchemy_sugerencia_repository import SQLAlchemySugerenciaRepository
from infrastructure.sqlalchemy_perfil_repository import SQLAlchemyPerfilRepository
from infrastructure.sqlalchemy_convocatoria_repository import SQLAlchemyConvocatoriaRepository
from frameworks.sqlalchemy_orm.database import db

matching_blueprint = Blueprint('matching', __name__, url_prefix='/matching')

# Inyección de dependencias (DIP aplicado en el servicio)
sugerencia_repo = SQLAlchemySugerenciaRepository(db.session)
perfil_repo = SQLAlchemyPerfilRepository(db.session)
convocatoria_repo = SQLAlchemyConvocatoriaRepository(db.session)

matching_service = MatchingApplicationService(
    sugerencia_repo=sugerencia_repo,
    perfil_repo=perfil_repo,
    convocatoria_repo=convocatoria_repo
)


@matching_blueprint.route('/recomendaciones', methods=['GET'])
def recomendar_convocatorias():
    """
    SRP: Este controlador SOLO maneja la petición HTTP.
    Obtiene el usuario, llama al servicio y devuelve la respuesta.
    """
    try:
        # 1. Obtener usuario autenticado
        usuario_id = session.get('usuario_id')
        if not usuario_id:
            return jsonify({"error": "No autenticado"}), 401

        # 2. Obtener parámetros
        limit = request.args.get('limit', 10, type=int)
        if limit > 50:
            limit = 50

        # 3. Llamar al servicio (toda la lógica está ahí)
        recomendaciones = matching_service.recomendar_convocatorias(usuario_id, limit)

        # 4. Devolver respuesta
        return jsonify({
            "data": recomendaciones,
            "total": len(recomendaciones)
        }), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": f"Error interno: {str(e)}"}), 500