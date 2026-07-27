# frameworks/flask_mvc/routes/auth_routes.py
from flask import Blueprint, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
from frameworks.sqlalchemy_orm.database import db
from infrastructure.sqlalchemy_usuario_repository import SQLAlchemyUsuarioRepository
from domain.auth.usuario import Usuario

auth_blueprint = Blueprint('auth', __name__)
usuario_repo = SQLAlchemyUsuarioRepository(db.session)


@auth_blueprint.route('/register', methods=['POST'])
def register():
    """Registro de usuario."""
    try:
        datos = request.get_json()
        if not datos:
            return jsonify({"error": "Datos inválidos"}), 400

        # Validar campos requeridos
        required = ['email', 'password', 'nombre', 'apellido', 'rol']
        for campo in required:
            if campo not in datos:
                return jsonify({"error": f"Campo '{campo}' requerido"}), 400

        # Verificar que el email no esté registrado
        existing = usuario_repo.obtener_por_email(datos['email'])
        if existing:
            return jsonify({"error": "El email ya está registrado"}), 409

        # Crear usuario
        usuario = Usuario(
            id=None,
            email=datos['email'],
            password_hash=generate_password_hash(datos['password']),
            nombre=datos['nombre'],
            apellido=datos['apellido'],
            rol=datos['rol'],
            activo=True  # Para pruebas, activar automáticamente
        )

        usuario_guardado = usuario_repo.guardar(usuario)

        return jsonify({
            "id": usuario_guardado.id,
            "email": usuario_guardado.email,
            "nombre": usuario_guardado.nombre,
            "apellido": usuario_guardado.apellido,
            "rol": usuario_guardado.rol,
            "message": "Usuario registrado exitosamente"
        }), 201

    except Exception as e:
        return jsonify({"error": f"Error interno: {str(e)}"}), 500


@auth_blueprint.route('/login', methods=['POST'])
def login():
    """Inicio de sesión."""
    try:
        datos = request.get_json()
        if not datos or 'email' not in datos or 'password' not in datos:
            return jsonify({"error": "Email y password requeridos"}), 400

        # Buscar usuario por email
        usuario = usuario_repo.obtener_por_email(datos['email'])
        if not usuario:
            return jsonify({"error": "Credenciales inválidas"}), 401

        # Verificar password
        if not check_password_hash(usuario.password_hash, datos['password']):
            return jsonify({"error": "Credenciales inválidas"}), 401

        # Verificar que esté activo
        if not usuario.activo:
            return jsonify({"error": "Cuenta no activada"}), 403

        # Guardar en sesión
        session['usuario_id'] = usuario.id
        session['usuario_rol'] = usuario.rol

        return jsonify({
            "id": usuario.id,
            "email": usuario.email,
            "nombre": usuario.nombre,
            "apellido": usuario.apellido,
            "rol": usuario.rol,
            "message": "Login exitoso"
        }), 200

    except Exception as e:
        return jsonify({"error": f"Error interno: {str(e)}"}), 500


@auth_blueprint.route('/logout', methods=['POST'])
def logout():
    """Cierre de sesión."""
    session.clear()
    return jsonify({"message": "Logout exitoso"}), 200


@auth_blueprint.route('/me', methods=['GET'])
def me():
    """Obtener usuario autenticado."""
    usuario_id = session.get('usuario_id')
    if not usuario_id:
        return jsonify({"error": "No autenticado"}), 401

    usuario = usuario_repo.obtener_por_id(usuario_id)
    if not usuario:
        return jsonify({"error": "Usuario no encontrado"}), 404

    return jsonify({
        "id": usuario.id,
        "email": usuario.email,
        "nombre": usuario.nombre,
        "apellido": usuario.apellido,
        "rol": usuario.rol
    }), 200