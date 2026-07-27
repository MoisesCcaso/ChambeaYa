import os

from dotenv import load_dotenv


load_dotenv()


def env_bool(name, default=False):
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///chambeaya.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    APP_URL = os.getenv("APP_URL", "http://127.0.0.1:5000")
    MAIL_DELIVERY_MODE = os.getenv("MAIL_DELIVERY_MODE", "console").lower()
    MAIL_SERVER = os.getenv("MAIL_SERVER")
    MAIL_PORT = int(os.getenv("MAIL_PORT", "587"))
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    MAIL_USE_TLS = env_bool("MAIL_USE_TLS", True)
    MAIL_USE_SSL = env_bool("MAIL_USE_SSL", False)
    MAIL_SENDER = os.getenv(
        "MAIL_SENDER",
        "ChambeaYa <no-reply@chambeaya.local>",
    )
    MAIL_TIMEOUT = int(os.getenv("MAIL_TIMEOUT", "15"))
    EXPOSE_AUTH_TOKENS = env_bool("EXPOSE_AUTH_TOKENS", False)
    DEMO_MODE = False


class DevelopmentConfig(Config):
    DEBUG = True
    EXPOSE_AUTH_TOKENS = env_bool(
        "EXPOSE_AUTH_TOKENS",
        Config.MAIL_DELIVERY_MODE != "smtp",
    )


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.getenv("TEST_DATABASE_URL", "sqlite:///:memory:")
    EXPOSE_AUTH_TOKENS = True
    MAIL_DELIVERY_MODE = "console"


class DemoConfig(Config):
    DEBUG = False
    DEMO_MODE = True
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "sqlite:///chambeaya-demo.db",
    )
    EXPOSE_AUTH_TOKENS = True
    MAIL_DELIVERY_MODE = "console"


class ProductionConfig(Config):
    DEBUG = False
    SESSION_COOKIE_SECURE = True


config_by_name = {
    "development": DevelopmentConfig,
    "demo": DemoConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
