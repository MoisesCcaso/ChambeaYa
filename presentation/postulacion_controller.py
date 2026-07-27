# presentation/postulacion_controller.py
from flask import Blueprint, request, jsonify, session
from application.postulacion_application_service import PostulacionApplicationService
from infrastructure.sqlalchemy_postulacion_repository import SQLAlchemyPostulacionRepository
from infrastructure.sqlalchemy_convocatoria_repository import SQLAlchemyConvocatoriaRepository
from infrastructure.sqlalchemy_perfil_repository import SQLAlchemyPerfilRepository
from frameworks.sqlalchemy_orm.database import db

# Crear blueprint
postulacion_blueprint = Blueprint('postulacion', __name__, url_prefix='/postulaciones')

# Inicializar dependencias
postulacion_repo = SQLAlchemyPostulacionRepository(db.session)
convocatoria_repo = SQLAlchemyConvocatoriaRepository(db.session)
perfil_repo = SQLAlchemyPerfilRepository(db.session)

postulacion_service = PostulacionApplicationService(
    postulacion_repo=postulacion_repo,
    convocatoria_repo=convocatoria_repo,
    perfil_repo=perfil_repo
)

@postulacion_blueprint.route('', methods=['POST'])
def crear_postulacion():
    """
    ESTILO ERROR/EXCEPTION HANDLING:
    Cada tipo de error se captura con su excepción específica
    y se devuelve una respuesta HTTP apropiada.
    """
    try:
        # 1. Validar autenticación
        usuario_id = session.get('usuario_id')
        usuario_rol = session.get('usuario_rol', 'practicante')
        
        if not usuario_id:
            return jsonify({"error": "No autenticado"}), 401
        
        if usuario_rol != 'practicante':
            return jsonify({"error": "Solo los practicantes pueden postularse"}), 403
        
        # 2. Validar datos de entrada
        datos = request.get_json()
        if not datos or 'convocatoria_id' not in datos:
            return jsonify({"error": "Campo 'convocatoria_id' requerido"}), 400
        
        # 3. Ejecutar la lógica de negocio
        resultado = postulacion_service.postularse(
            practicante_id=usuario_id,
            convocatoria_id=datos['convocatoria_id'],
            mensaje=datos.get('mensaje', ''),
            archivos=datos.get('archivos', [])
        )
        
        return jsonify(resultado), 201
        
    # 4. Errores de negocio (400 Bad Request)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    
    # 5. Errores de permisos (403 Forbidden)
    except PermissionError as e:
        return jsonify({"error": str(e)}), 403
    
    # 6. Errores inesperados (500 Internal Server Error)
    except Exception as e:
        app.logger.error(f"Error inesperado: {str(e)}")
        return jsonify({"error": "Error interno del servidor"}), 500

@postulacion_blueprint.route('/me', methods=['GET'])
def mis_postulaciones():
    try:
        usuario_id = session.get('usuario_id')
        if not usuario_id:
            return jsonify({"error": "No autenticado"}), 401
        postulaciones = postulacion_service.obtener_postulaciones_practicante(usuario_id)
        return jsonify({"data": postulaciones, "total": len(postulaciones)}), 200
    except Exception as e:
        return jsonify({"error": f"Error interno: {str(e)}"}), 500


@postulacion_blueprint.route('/convocatoria/<int:convocatoria_id>', methods=['GET'])
def postulaciones_convocatoria(convocatoria_id):
    try:
        usuario_id = session.get('usuario_id')
        usuario_rol = session.get('usuario_rol')
        if not usuario_id:
            return jsonify({"error": "No autenticado"}), 401
        if usuario_rol != 'empresa':
            return jsonify({"error": "Solo las empresas pueden ver postulantes"}), 403
        postulaciones = postulacion_service.obtener_postulaciones_convocatoria(convocatoria_id)
        return jsonify({"data": postulaciones, "total": len(postulaciones)}), 200
    except Exception as e:
        return jsonify({"error": f"Error interno: {str(e)}"}), 500


@postulacion_blueprint.route('/<int:postulacion_id>/estado', methods=['PATCH'])
def actualizar_estado_postulacion(postulacion_id):
    try:
        usuario_id = session.get('usuario_id')
        usuario_rol = session.get('usuario_rol')
        if not usuario_id:
            return jsonify({"error": "No autenticado"}), 401
        if usuario_rol != 'empresa':
            return jsonify({"error": "Solo las empresas pueden cambiar el estado"}), 403
        
        datos = request.get_json()
        if not datos or 'estado' not in datos:
            return jsonify({"error": "Campo 'estado' requerido"}), 400
        
        resultado = postulacion_service.actualizar_estado(
            postulacion_id=postulacion_id,
            nuevo_estado=datos['estado'],
            usuario_rol=usuario_rol
        )
        return jsonify(resultado), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except PermissionError as e:
        return jsonify({"error": str(e)}), 403
    except Exception as e:
        return jsonify({"error": f"Error interno: {str(e)}"}), 500


@postulacion_blueprint.route('/<int:postulacion_id>', methods=['DELETE'])
def retirar_postulacion(postulacion_id):
    try:
        usuario_id = session.get('usuario_id')
        if not usuario_id:
            return jsonify({"error": "No autenticado"}), 401
        resultado = postulacion_service.retirar_postulacion(postulacion_id, usuario_id)
        if resultado:
            return jsonify({"message": "Postulación retirada exitosamente"}), 200
        return jsonify({"error": "No se pudo retirar la postulación"}), 400
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except PermissionError as e:
        return jsonify({"error": str(e)}), 403
    except Exception as e:
        return jsonify({"error": f"Error interno: {str(e)}"}), 500