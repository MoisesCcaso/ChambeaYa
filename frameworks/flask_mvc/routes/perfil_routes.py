# frameworks/flask_mvc/routes/perfil_routes.py
from flask import Blueprint, request, jsonify

perfil_blueprint = Blueprint('perfil', __name__)

@perfil_blueprint.route('/me', methods=['GET'])
def get_perfil():
    return jsonify({"message": "Perfil del usuario"}), 200

@perfil_blueprint.route('/me', methods=['PUT'])
def update_perfil():
    return jsonify({"message": "Perfil actualizado"}), 200 