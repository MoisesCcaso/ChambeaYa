# presentation/matching_controller.py
from flask import Blueprint, request, jsonify, session
from application.matching_application_service import MatchingApplicationService
from infrastructure.sqlalchemy_sugerencia_repository import SQLAlchemySugerenciaRepository
from infrastructure.sqlalchemy_perfil_repository import SQLAlchemyPerfilRepository
from infrastructure.sqlalchemy_convocatoria_repository import SQLAlchemyConvocatoriaRepository
from frameworks.sqlalchemy_orm.database import db

# Crear blueprint
matching_blueprint = Blueprint('matching', __name__, url_prefix='/matching')

# Inicializar dependencias
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
    Obtiene convocatorias recomendadas para el practicante autenticado.
    """
    try:
        # Obtener usuario autenticado (asumimos que está en la sesión)
        usuario_id = session.get('usuario_id')
        if not usuario_id:
            return jsonify({"error": "No autenticado"}), 401
        
        # Obtener parámetros de consulta
        limit = request.args.get('limit', 10, type=int)
        if limit > 50:
            limit = 50
        
        # Obtener recomendaciones
        recomendaciones = matching_service.recomendar_convocatorias(usuario_id, limit)
        
        return jsonify({
            "data": recomendaciones,
            "total": len(recomendaciones)
        }), 200
        
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": f"Error interno: {str(e)}"}), 500