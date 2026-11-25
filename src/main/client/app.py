import os

from dotenv import load_dotenv
from flask import Flask
from flask_wtf.csrf import CSRFProtect

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
    # The client only serves GET views (writes go to the API, which has its own CSRF check);
    # this still rejects any unsafe method that a future view might add without a token (Sonar S4502).
    CSRFProtect(app)
    app.register_blueprint(web_bp)
    return app
