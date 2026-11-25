"""I-02 - Tests for the SQLAlchemy user repository with in-memory SQLite.

Code under test: identity/infrastructure/sqlalchemy_user_repository.py
"""
from datetime import datetime, timedelta, timezone

from identity.domain.expiring_token import ExpiringToken
from identity.domain.user import User
from identity.infrastructure.sqlalchemy_user_repository import SqlAlchemyUserRepository


def sample_user(*, email="usuario@test.local", role=User.ROLE_INTERN):
    return User(
        email=email,
        password_hash="hash-prueba",
        role=role,
        status=User.STATUS_PENDING,
    )


def test_save_and_find_user_by_email(app_context):
    repository = SqlAlchemyUserRepository()
    user = repository.save(sample_user(email="ana@test.local"))

    found = repository.find_by_email("ana@test.local")

    assert found is not None
    assert found.id == user.id
    assert found.email == "ana@test.local"
    assert found.role == User.ROLE_INTERN
    assert found.status == User.STATUS_PENDING


def test_save_and_find_user_by_id(app_context):
    repository = SqlAlchemyUserRepository()
    user = repository.save(sample_user(email="juan@test.local"))

    found = repository.find_by_id(user.id)

    assert found is not None
    assert found.id == user.id
    assert found.email == "juan@test.local"


def test_find_missing_email_returns_none(app_context):
    repository = SqlAlchemyUserRepository()

    assert repository.find_by_email("no-existe@test.local") is None
    assert repository.find_by_id(99999) is None


def test_save_and_query_activation_token(app_context):
    repository = SqlAlchemyUserRepository()
    expires_at = datetime.now(timezone.utc) + timedelta(hours=48)
    user = sample_user(email="activar@test.local")
    user.assign_activation_token(ExpiringToken("tok-activar", expires_at))
    saved = repository.save(user)

    found = repository.find_by_activation_token("tok-activar")

    assert found is not None
    assert found.id == saved.id
    assert found.activation_token == "tok-activar"
    assert found.activation_token_expires_at == expires_at.replace(tzinfo=None)


def test_missing_activation_token_returns_none(app_context):
    repository = SqlAlchemyUserRepository()

    assert repository.find_by_activation_token("token-inexistente") is None


def test_save_and_query_password_reset_token(app_context):
    repository = SqlAlchemyUserRepository()
    expires_at = datetime.now(timezone.utc) + timedelta(hours=2)
    user = sample_user(email="recuperar@test.local")
    user.assign_password_reset_token(ExpiringToken("tok-recuperar", expires_at))
    saved = repository.save(user)

    found = repository.find_by_password_reset_token("tok-recuperar")

    assert found is not None
    assert found.id == saved.id
    assert found.password_reset_token == "tok-recuperar"
    assert found.password_reset_expires_at == expires_at.replace(tzinfo=None)


def test_missing_password_reset_token_returns_none(app_context):
    repository = SqlAlchemyUserRepository()

    assert repository.find_by_password_reset_token("token-inexistente") is None
