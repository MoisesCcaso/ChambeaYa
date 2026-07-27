# frameworks/flask_mvc/routes/health_routes.py
from flask import Blueprint, jsonify

health_blueprint = Blueprint('health', __name__)

@health_blueprint.route('/health', methods=['GET'])
def health_check():
    """Endpoint para verificar que la aplicación está funcionando."""
    return jsonify({
        "status": "ok",
        "message": "ChambeaYa API está funcionando correctamente"
    }), 200