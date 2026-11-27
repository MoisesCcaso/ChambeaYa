from identity.controllers.auth_routes import auth_bp
from certification.controllers.certificate_routes import certificate_bp
from bootstrap.health_routes import health_bp
from matching.controllers.matching_routes import matching_bp
from notifications.controllers.notification_routes import notification_bp
from profiles.controllers.profile_routes import profile_bp
from internships.controllers.internship_routes import internship_bp
from recruitment.controllers.job_posting_routes import job_posting_bp
from recruitment.controllers.job_application_routes import job_application_bp
from bootstrap.openapi import openapi_json


def register_routes(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(certificate_bp)
    app.register_blueprint(job_posting_bp)
    app.register_blueprint(notification_bp)
    app.register_blueprint(job_application_bp)
    app.register_blueprint(health_bp)
    app.register_blueprint(matching_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(internship_bp)
    app.add_url_rule(
        "/openapi.json",
        endpoint="openapi_json",
        view_func=openapi_json,
        methods=["GET"],
    )
