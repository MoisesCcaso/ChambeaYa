"""Fixtures shared by the project's tests."""

import pytest

from bootstrap.app import create_app
from shared.database import db


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
