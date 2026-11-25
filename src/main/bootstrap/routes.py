from identity.presentation.auth_routes import auth_bp
from frameworks.flask_mvc.routes.certificado_routes import certificado_bp
from bootstrap.health_routes import health_bp
from matching.presentation.matching_routes import matching_bp
from notifications.presentation.notification_routes import notification_bp
from profiles.presentation.profile_routes import profile_bp
from frameworks.flask_mvc.routes.practica_routes import practica_bp
from recruitment.presentation.job_posting_routes import job_posting_bp
from recruitment.presentation.job_application_routes import job_application_bp
from bootstrap.web_routes import web_bp


def register_routes(app):
    app.register_blueprint(web_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(certificado_bp)
    app.register_blueprint(job_posting_bp)
    app.register_blueprint(notification_bp)
    app.register_blueprint(job_application_bp)
    app.register_blueprint(health_bp)
    app.register_blueprint(matching_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(practica_bp)
