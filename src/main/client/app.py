import os

from dotenv import load_dotenv
from flask import Flask

from client.views import web_bp


def _env_bool(name, default):
    value = os.getenv(name)
    return default if value is None else value.strip().lower() in {"1", "true", "yes", "on"}


def create_app(overrides=None):
    load_dotenv()
    app = Flask(__name__, static_folder="static", template_folder="templates")
    app.config.update(
        API_URL=os.getenv("API_URL", "http://127.0.0.1:5000").rstrip("/"),
        DEMO_MODE=_env_bool("DEMO_MODE", os.getenv("FLASK_ENV") == "demo"),
        DEMO_PASSWORD=os.getenv("DEMO_PASSWORD"),
    )
    app.config.update(overrides or {})
    app.register_blueprint(web_bp)
    return app
