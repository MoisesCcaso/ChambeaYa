import os

from flask import Flask

from config import config_by_name
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

    db.init_app(app)
    migrate.init_app(app, db, directory="frameworks/migrations")

    register_routes(app)

    return app
