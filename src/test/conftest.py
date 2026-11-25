"""Fixtures shared by the project's tests."""

import pytest

from bootstrap.app import create_app
from shared.database import db


@pytest.fixture(autouse=True)
def close_database_connections():
    """Closes the SQLite connections of every app a test created.

    Each test builds its own app with an in-memory database; without this, the garbage
    collector closes them later and Python >= 3.13 reports "ResourceWarning: unclosed database".
    """
    yield
    # _app_engines is Flask-SQLAlchemy's registry of engines per app (no public way to list them).
    for engines in list(db._app_engines.values()):
        for engine in engines.values():
            engine.dispose()


@pytest.fixture
def app(tmp_path):
    """Creates an isolated app with in-memory SQLite for each test."""
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
    """Test HTTP client bound to the isolated app."""
    return app.test_client()


@pytest.fixture
def app_context(app):
    """App context for tests that query SQLAlchemy directly."""
    with app.app_context():
        yield
