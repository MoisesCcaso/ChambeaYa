from frameworks.flask_mvc.routes.health_routes import health_bp


def register_routes(app):
    app.register_blueprint(health_bp)
