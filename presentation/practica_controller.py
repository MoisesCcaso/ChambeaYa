# presentation/practica_controller.py
from flask import Blueprint, jsonify

practica_blueprint = Blueprint('practica', __name__, url_prefix='/practicas')

@practica_blueprint.route('', methods=['GET'])
def listar_practicas():
    return jsonify({"message": "Listar prácticas"}), 200