# presentation/entregable_controller.py
from flask import Blueprint, jsonify

entregable_blueprint = Blueprint('entregable', __name__, url_prefix='/entregables')

@entregable_blueprint.route('', methods=['GET'])
def listar_entregables():
    return jsonify({"message": "Listar entregables"}), 200