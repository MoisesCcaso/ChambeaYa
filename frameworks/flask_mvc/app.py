import os

from flask import Flask, jsonify
from sqlalchemy.exc import IntegrityError

from config import config_by_name
from frameworks.flask_mvc.demo import register_demo_commands
from frameworks.flask_mvc.email_cli import register_email_commands
from frameworks.flask_mvc.routes import register_routes
from frameworks.sqlalchemy_orm import models  # noqa: F401
from frameworks.sqlalchemy_orm.database import db, migrate


def create_app(config_name=None):
    app = Flask(
        __name__,
        instance_relative_config=True,
        static_folder="static",
        template_folder="templates",
    )

    selected_config = config_name or os.getenv("FLASK_ENV", "default")
    app.config.from_object(config_by_name.get(selected_config, config_by_name["default"]))
    if selected_config == "production" and app.config["SECRET_KEY"] == "dev-secret-key":
        raise RuntimeError("SECRET_KEY debe configurarse en producción")
    app.config.setdefault(
        "UPLOAD_FOLDER",
        os.path.join(app.instance_path, "uploads", "entregables"),
    )
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    db.init_app(app)
    migrate.init_app(app, db, directory="frameworks/migrations")

    register_routes(app)
    register_demo_commands(app)
    register_email_commands(app)

    @app.errorhandler(IntegrityError)
    def handle_integrity_error(_error):
        db.session.rollback()
        return jsonify({"error": "El registro ya existe o contiene datos en conflicto"}), 409

    @app.errorhandler(413)
    def handle_payload_too_large(_error):
        return jsonify({"error": "El archivo excede el límite de 10 MB"}), 413

    return app
