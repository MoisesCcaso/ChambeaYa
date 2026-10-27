"""Fixtures compartidas para las pruebas del proyecto."""

import pytest

from frameworks.flask_mvc.app import create_app
from frameworks.sqlalchemy_orm.database import db


@pytest.fixture
def app(tmp_path):
    """Crea una aplicación aislada con SQLite en memoria para cada prueba."""
    application = create_app("testing")
    application.config.update(
        TESTING=True,
        SECRET_KEY="testing-secret",
        UPLOAD_FOLDER=str(tmp_path),
    )

    with application.app_context():
        db.create_all()

    yield application

    with application.app_context():
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Cliente HTTP de prueba asociado a la aplicación aislada."""
    return app.test_client()


@pytest.fixture
def app_context(app):
    """Contexto de aplicación para pruebas que consultan SQLAlchemy directamente."""
    with app.app_context():
        yield
