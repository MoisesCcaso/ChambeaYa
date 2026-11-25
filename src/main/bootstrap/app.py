import os
from pathlib import Path

from flask import Flask
from flask_wtf.csrf import CSRFProtect

from config import config_by_name
from bootstrap.demo import register_demo_commands
from bootstrap.email_cli import register_email_commands
from bootstrap.error_handlers import register_error_handlers
from bootstrap.routes import register_routes
from bootstrap import models  # noqa: F401
from shared.database import db, migrate

csrf = CSRFProtect()


def create_app(config_name=None):
    project_root = Path(__file__).resolve().parents[3]
    instance_path = project_root / "instance"
    app = Flask(
        __name__,
        instance_path=str(instance_path),
        instance_relative_config=True,
        static_folder="static",
        template_folder="templates",
    )

    selected_config = config_name or os.getenv("FLASK_ENV", "default")
    app.config.from_object(config_by_name.get(selected_config, config_by_name["default"]))
    if not app.config.get("SECRET_KEY"):
        raise RuntimeError("SECRET_KEY debe configurarse en producción")
    app.config.setdefault(
        "UPLOAD_FOLDER",
        os.path.join(app.instance_path, "uploads", "entregables"),
    )
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    db.init_app(app)
    csrf.init_app(app)
    migrations_directory = Path(__file__).resolve().parent / "migrations"
    migrate.init_app(app, db, directory=str(migrations_directory))

    register_routes(app)
    register_demo_commands(app)
    register_email_commands(app)
    register_error_handlers(app)
    return app
