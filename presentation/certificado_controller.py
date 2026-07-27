# presentation/certificado_controller.py
from flask import Blueprint, request, jsonify, session
from application.certificacion_application_service import CertificacionApplicationService
from infrastructure.sqlalchemy_certificado_repository import SQLAlchemyCertificadoRepository, SQLAlchemyReputacionRepository
from infrastructure.sqlalchemy_practica_repository import SQLAlchemyPracticaRepository
from infrastructure.sqlalchemy_postulacion_repository import SQLAlchemyPostulacionRepository
from infrastructure.sqlalchemy_evaluacion_repository import SQLAlchemyEvaluacionRepository
from frameworks.sqlalchemy_orm.database import db

certificado_blueprint = Blueprint('certificado', __name__, url_prefix='/certificados')

# Inicializar dependencias
certificado_repo = SQLAlchemyCertificadoRepository(db.session)
reputacion_repo = SQLAlchemyReputacionRepository(db.session)
practica_repo = SQLAlchemyPracticaRepository(db.session)
postulacion_repo = SQLAlchemyPostulacionRepository(db.session)
evaluacion_repo = SQLAlchemyEvaluacionRepository(db.session)

certificacion_service = CertificacionApplicationService(
    certificado_repo=certificado_repo,
    reputacion_repo=reputacion_repo,
    practica_repo=practica_repo,
    postulacion_repo=postulacion_repo,
    evaluacion_repo=evaluacion_repo
)


@certificado_blueprint.route('/generar/<int:practica_id>', methods=['POST'])
def generar_certificado(practica_id):
    """Genera un certificado para una práctica completada (solo empresa)."""
    try:
        usuario_id = session.get('usuario_id')
        usuario_rol = session.get('usuario_rol')

        if not usuario_id:
            return jsonify({"error": "No autenticado"}), 401

        if usuario_rol != 'empresa':
            return jsonify({"error": "Solo las empresas pueden generar certificados"}), 403

        certificado = certificacion_service.generar_certificado(practica_id)
        return jsonify(certificado.to_dict()), 201

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Error interno: {str(e)}"}), 500


@certificado_blueprint.route('/me', methods=['GET'])
def mis_certificados():
    """Obtiene todos los certificados del practicante autenticado."""
    try:
        usuario_id = session.get('usuario_id')
        if not usuario_id:
            return jsonify({"error": "No autenticado"}), 401

        certificados = certificacion_service.obtener_certificados_practicante(usuario_id)
        return jsonify({
            "data": certificados,
            "total": len(certificados)
        }), 200

    except Exception as e:
        return jsonify({"error": f"Error interno: {str(e)}"}), 500


@certificado_blueprint.route('/verificar/<codigo>', methods=['GET'])
def verificar_certificado(codigo):
    """Verifica la validez de un certificado (público)."""
    try:
        resultado = certificacion_service.verificar_certificado(codigo)
        return jsonify(resultado), 200 if resultado['valido'] else 404

    except Exception as e:
        return jsonify({"error": f"Error interno: {str(e)}"}), 500


@certificado_blueprint.route('/revocar/<int:certificado_id>', methods=['POST'])
def revocar_certificado(certificado_id):
    """Revoca un certificado (solo admin)."""
    try:
        usuario_id = session.get('usuario_id')
        usuario_rol = session.get('usuario_rol')

        if not usuario_id:
            return jsonify({"error": "No autenticado"}), 401

        if usuario_rol != 'admin':
            return jsonify({"error": "Solo administradores pueden revocar certificados"}), 403

        datos = request.get_json()
        if not datos or 'motivo' not in datos:
            return jsonify({"error": "Campo 'motivo' requerido"}), 400

        certificado = certificacion_service.revocar_certificado(certificado_id, datos['motivo'])
        return jsonify(certificado.to_dict()), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Error interno: {str(e)}"}), 500


@certificado_blueprint.route('/reputacion/me', methods=['GET'])
def mi_reputacion():
    """Obtiene la reputación del usuario autenticado."""
    try:
        usuario_id = session.get('usuario_id')
        if not usuario_id:
            return jsonify({"error": "No autenticado"}), 401

        reputacion = certificacion_service.obtener_reputacion(usuario_id)
        return jsonify(reputacion), 200

    except Exception as e:
        return jsonify({"error": f"Error interno: {str(e)}"}), 500


@certificado_blueprint.route('/reputacion/top', methods=['GET'])
def top_reputacion():
    """Obtiene el top de practicantes por reputación (público)."""
    try:
        limit = request.args.get('limit', 10, type=int)
        if limit > 50:
            limit = 50

        top = certificacion_service.obtener_top_reputacion(limit)
        return jsonify({
            "data": top,
            "total": len(top)
        }), 200

    except Exception as e:
        return jsonify({"error": f"Error interno: {str(e)}"}), 500


@certificado_blueprint.route('/reputacion/usuario/<int:usuario_id>', methods=['GET'])
def reputacion_usuario(usuario_id):
    """Obtiene la reputación de un usuario específico (público)."""
    try:
        reputacion = certificacion_service.obtener_reputacion(usuario_id)
        return jsonify(reputacion), 200

    except Exception as e:
        return jsonify({"error": f"Error interno: {str(e)}"}), 500