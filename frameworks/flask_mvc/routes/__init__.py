# frameworks/flask_mvc/routes/__init__.py
from .health_routes import health_blueprint
from .auth_routes import auth_blueprint
from .perfil_routes import perfil_blueprint

__all__ = [
    'health_blueprint',
    'auth_blueprint',
    'perfil_blueprint'
]