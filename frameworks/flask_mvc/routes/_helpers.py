from functools import wraps

from flask import jsonify, session

UNAUTHORIZED_MESSAGE = "No autenticado"


def current_user_id():
    return session.get("usuario_id")


def login_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        usuario_id = current_user_id()
        if usuario_id is None:
            return jsonify({"error": UNAUTHORIZED_MESSAGE}), 401

        return view(usuario_id, *args, **kwargs)

    return wrapper
