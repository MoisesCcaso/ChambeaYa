from frameworks.flask_mvc.routes.auth_routes import auth_bp
from frameworks.flask_mvc.routes.certificado_routes import certificado_bp
from frameworks.flask_mvc.routes.health_routes import health_bp
from frameworks.flask_mvc.routes.matching_routes import matching_bp
from frameworks.flask_mvc.routes.perfil_routes import perfil_bp
from frameworks.flask_mvc.routes.practica_routes import practica_bp
from frameworks.flask_mvc.routes.convocatoria_routes import convocatoria_bp
from frameworks.flask_mvc.routes.postulacion_routes import postulacion_bp


def register_routes(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(certificado_bp)
    app.register_blueprint(convocatoria_bp)
    app.register_blueprint(postulacion_bp)
    app.register_blueprint(health_bp)
    app.register_blueprint(matching_bp)
    app.register_blueprint(perfil_bp)
    app.register_blueprint(practica_bp)
    app.register_blueprint(certificado_bp)