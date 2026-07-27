# presentation/reporte_controller.py
from flask import Blueprint, request, jsonify, session
from application.reporte_application_service import ReporteApplicationService
from infrastructure.sqlalchemy_usuario_repository import SQLAlchemyUsuarioRepository
from infrastructure.sqlalchemy_convocatoria_repository import SQLAlchemyConvocatoriaRepository
from infrastructure.sqlalchemy_postulacion_repository import SQLAlchemyPostulacionRepository
from infrastructure.sqlalchemy_practica_repository import SQLAlchemyPracticaRepository
from infrastructure.sqlalchemy_certificado_repository import SQLAlchemyReputacionRepository
from frameworks.sqlalchemy_orm.database import db

reporte_blueprint = Blueprint('reporte', __name__, url_prefix='/reportes')

# Inicializar dependencias
usuario_repo = SQLAlchemyUsuarioRepository(db.session)
convocatoria_repo = SQLAlchemyConvocatoriaRepository(db.session)
postulacion_repo = SQLAlchemyPostulacionRepository(db.session)
practica_repo = SQLAlchemyPracticaRepository(db.session)
reputacion_repo = SQLAlchemyReputacionRepository(db.session)

reporte_service = ReporteApplicationService(
    usuario_repo=usuario_repo,
    convocatoria_repo=convocatoria_repo,
    postulacion_repo=postulacion_repo,
    practica_repo=practica_repo,
    reputacion_repo=reputacion_repo
)


@reporte_blueprint.route('/dashboard', methods=['GET'])
def dashboard_admin():
    """Dashboard del administrador."""
    try:
        usuario_id = session.get('usuario_id')
        usuario_rol = session.get('usuario_rol')
    
        if not usuario_id:
            return jsonify({"error": "No autenticado"}), 401

        if usuario_rol != 'admin':
            return jsonify({"error": "Solo administradores pueden acceder al dashboard"}), 403

        dashboard = reporte_service.generar_dashboard_admin()
        return jsonify(dashboard), 200

    except Exception as e:
        return jsonify({"error": f"Error interno: {str(e)}"}), 500


@reporte_blueprint.route('/postulaciones', methods=['GET'])
def reporte_postulaciones():
    """Reporte de postulaciones por período."""
    try:
        usuario_id = session.get('usuario_id')
        usuario_rol = session.get('usuario_rol')

        if not usuario_id:
            return jsonify({"error": "No autenticado"}), 401

        if usuario_rol not in ['admin', 'empresa']:
            return jsonify({"error": "Acceso no autorizado"}), 403

        # Parámetros
        fecha_inicio = request.args.get('fecha_inicio')
        fecha_fin = request.args.get('fecha_fin')
        empresa_id = request.args.get('empresa_id', type=int)

        if not fecha_inicio or not fecha_fin:
            return jsonify({"error": "Parámetros 'fecha_inicio' y 'fecha_fin' requeridos"}), 400

        reporte = reporte_service.generar_reporte_postulaciones(
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            empresa_id=empresa_id if usuario_rol == 'admin' else usuario_id
        )

        return jsonify(reporte), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Error interno: {str(e)}"}), 500


@reporte_blueprint.route('/practicas', methods=['GET'])
def reporte_practicas():
    """Reporte de prácticas por período."""
    try:
        usuario_id = session.get('usuario_id')
        usuario_rol = session.get('usuario_rol')

        if not usuario_id:
            return jsonify({"error": "No autenticado"}), 401

        if usuario_rol not in ['admin', 'empresa']:
            return jsonify({"error": "Acceso no autorizado"}), 403

        fecha_inicio = request.args.get('fecha_inicio')
        fecha_fin = request.args.get('fecha_fin')
        empresa_id = request.args.get('empresa_id', type=int)

        if not fecha_inicio or not fecha_fin:
            return jsonify({"error": "Parámetros 'fecha_inicio' y 'fecha_fin' requeridos"}), 400

        reporte = reporte_service.generar_reporte_practicas(
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            empresa_id=empresa_id if usuario_rol == 'admin' else usuario_id
        )

        return jsonify(reporte), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Error interno: {str(e)}"}), 500


@reporte_blueprint.route('/convocatorias', methods=['GET'])
def reporte_convocatorias():
    """Reporte de convocatorias."""
    try:
        usuario_id = session.get('usuario_id')
        usuario_rol = session.get('usuario_rol')

        if not usuario_id:
            return jsonify({"error": "No autenticado"}), 401

        if usuario_rol not in ['admin', 'empresa']:
            return jsonify({"error": "Acceso no autorizado"}), 403

        empresa_id = request.args.get('empresa_id', type=int)

        reporte = reporte_service.generar_reporte_convocatorias(
            empresa_id=empresa_id if usuario_rol == 'admin' else usuario_id
        )

        return jsonify(reporte), 200

    except Exception as e:
        return jsonify({"error": f"Error interno: {str(e)}"}), 500


@reporte_blueprint.route('/reputacion', methods=['GET'])
def reporte_reputacion():
    """Reporte de top reputación (público)."""
    try:
        limit = request.args.get('limit', 10, type=int)
        if limit > 50:
            limit = 50

        reporte = reporte_service.generar_reporte_reputacion(limit)
        return jsonify(reporte), 200

    except Exception as e:
        return jsonify({"error": f"Error interno: {str(e)}"}), 500  