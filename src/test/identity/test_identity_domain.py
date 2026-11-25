"""Unit tests for the identity domain rules."""

import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

from werkzeug.security import check_password_hash

from identity.domain.authentication_domain_service import AuthenticationDomainService
from identity.domain.expiring_token import ExpiringToken
from identity.domain.user import User
from identity.domain.i_password_hasher import IPasswordHasher
from identity.infrastructure.werkzeug_password_hasher import WerkzeugPasswordHasher

class FakeHasher(IPasswordHasher):
    """Test double: lets the domain be tested without werkzeug."""

    def hash(self, password):
        return f"hash:{password}"

    def verify(self, password_hash, password):
        return password_hash == f"hash:{password}"

class UserTest(unittest.TestCase):
    def test_register_valid_user_returns_the_same_user(self):
        user = User(
            email="persona@example.com",
            password_hash="hash-seguro",
            role=User.ROLE_INTERN,
        )

        result = user.register()

        self.assertIs(result, user)
        self.assertEqual(user.status, User.STATUS_PENDING)

    def test_register_rejects_missing_email(self):
        user = User(password_hash="hash-seguro", role=User.ROLE_COMPANY)

        with self.assertRaisesRegex(ValueError, "El email es obligatorio"):
            user.register()

    def test_register_rejects_missing_password(self):
        user = User(email="persona@example.com", role=User.ROLE_COMPANY)

        with self.assertRaisesRegex(ValueError, "La contraseña es obligatoria"):
            user.register()

    def test_register_rejects_invalid_role(self):
        user = User(
            email="persona@example.com",
            password_hash="hash-seguro",
            role="administrador",
        )

        with self.assertRaisesRegex(ValueError, "El tipo de usuario no es válido"):
            user.register()

    def test_login_rejects_inactive_user(self):
        user = User(status=User.STATUS_PENDING)

        with self.assertRaisesRegex(ValueError, "La cuenta no está activa"):
            user.login()

    def test_login_returns_active_user(self):
        user = User(status=User.STATUS_ACTIVE)

        self.assertIs(user.login(), user)

    def test_activate_changes_status_and_clears_activation_token(self):
        user = User(
            activation_token="token-activacion",
            activation_token_expires_at=datetime.now(timezone.utc),
        )

        result = user.activate()

        self.assertIs(result, user)
        self.assertEqual(user.status, User.STATUS_ACTIVE)
        self.assertIsNone(user.activation_token)
        self.assertIsNone(user.activation_token_expires_at)

    def test_assigning_tokens_stores_value_and_expiration(self):
        expires_at = datetime(2030, 1, 1, tzinfo=timezone.utc)
        user = User()
        activation = ExpiringToken("activacion", expires_at)
        password_reset = ExpiringToken("recuperacion", expires_at)

        self.assertIs(user.assign_activation_token(activation), user)
        self.assertIs(user.assign_password_reset_token(password_reset), user)

        self.assertEqual(user.activation_token, "activacion")
        self.assertEqual(user.activation_token_expires_at, expires_at)
        self.assertEqual(user.password_reset_token, "recuperacion")
        self.assertEqual(user.password_reset_expires_at, expires_at)
        self.assertIs(user.activation, activation)
        self.assertIs(user.password_reset, password_reset)
        self.assertTrue(user.has_valid_activation_token())
        self.assertTrue(user.has_valid_password_reset_token())

    def test_update_password_saves_hash_and_clears_password_reset_token(self):
        user = User(
            password_reset_token="token-anterior",
            password_reset_expires_at=datetime(2030, 1, 1, tzinfo=timezone.utc),
        )

        result = user.update_password("nuevo-hash")

        self.assertIs(result, user)
        self.assertEqual(user.password_hash, "nuevo-hash")
        self.assertIsNone(user.password_reset_token)
        self.assertIsNone(user.password_reset_expires_at)

    def test_update_password_rejects_empty_hash(self):
        user = User()

        with self.assertRaisesRegex(ValueError, "La contraseña es obligatoria"):
            user.update_password("")


class AuthenticationDomainServiceTest(unittest.TestCase):
    def setUp(self):
        self.service = AuthenticationDomainService(WerkzeugPasswordHasher())

    def test_generate_password_hash_accepts_8_and_128_character_limits(self):
        passwords = ("Abcdef1x", "A" + "b" * 126 + "1")

        for password in passwords:
            with self.subTest(length=len(password)):
                password_hash = self.service.generate_password_hash(password)
                self.assertNotEqual(password_hash, password)
                self.assertTrue(check_password_hash(password_hash, password))

    def test_generate_password_hash_rejects_empty_or_shorter_than_8(self):
        for password in (None, "Abcde1x"):
            with self.subTest(password=password):
                with self.assertRaises(ValueError):
                    self.service.generate_password_hash(password)

    def test_generate_password_hash_rejects_more_than_128_characters(self):
        password = "A" + "b" * 127 + "1"

        with self.assertRaisesRegex(ValueError, "no puede superar 128"):
            self.service.generate_password_hash(password)

    def test_generate_password_hash_requires_lowercase_uppercase_and_digit(self):
        invalid_passwords = ("ABCDEFG1", "abcdefg1", "Abcdefgh")

        for password in invalid_passwords:
            with self.subTest(password=password):
                with self.assertRaises(ValueError):
                    self.service.generate_password_hash(password)

    def test_authenticate_returns_false_without_user(self):
        self.assertFalse(self.service.authenticate(None, "Abcdefg1"))

    def test_authenticate_checks_password_of_active_user(self):
        password = "Abcdefg1"
        user = User(
            status=User.STATUS_ACTIVE,
            password_hash=self.service.generate_password_hash(password),
        )

        self.assertTrue(self.service.authenticate(user, password))
        self.assertFalse(self.service.authenticate(user, "OtraClave1"))

    def test_authenticate_rejects_inactive_user(self):
        user = User(
            status=User.STATUS_PENDING,
            password_hash=self.service.generate_password_hash("Abcdefg1"),
        )

        with self.assertRaisesRegex(ValueError, "La cuenta no está activa"):
            self.service.authenticate(user, "Abcdefg1")

    def test_generate_token_creates_value_and_expiration_for_requested_duration(self):
        before = datetime.now(timezone.utc)

        token = self.service.generate_token(valid_hours=2)

        after = datetime.now(timezone.utc)
        self.assertTrue(token.value)
        self.assertGreaterEqual(token.expires_at, before + timedelta(hours=2))
        self.assertLessEqual(token.expires_at, after + timedelta(hours=2))

    def test_validate_token_delegates_to_token_validity(self):
        now_value = datetime(2030, 1, 1, tzinfo=timezone.utc)
        valid = now_value + timedelta(minutes=1)
        expired = now_value - timedelta(minutes=1)

        with patch("identity.domain.expiring_token.datetime") as datetime_mock:
            datetime_mock.now.return_value = now_value
            self.assertTrue(self.service.validate_token("token", valid))
            self.assertFalse(self.service.validate_token("token", expired))


class ExpiringTokenTest(unittest.TestCase):
    def test_is_valid_for_future_expiration(self):
        now_value = datetime(2030, 1, 1, tzinfo=timezone.utc)

        with patch("identity.domain.expiring_token.datetime") as datetime_mock:
            datetime_mock.now.return_value = now_value
            self.assertTrue(ExpiringToken("token", now_value + timedelta(seconds=1)).is_valid())

    def test_is_valid_returns_false_for_expired_token(self):
        now_value = datetime(2030, 1, 1, tzinfo=timezone.utc)

        with patch("identity.domain.expiring_token.datetime") as datetime_mock:
            datetime_mock.now.return_value = now_value
            self.assertFalse(ExpiringToken("token", now_value - timedelta(seconds=1)).is_valid())

    def test_is_valid_returns_false_without_value_or_expiration(self):
        self.assertFalse(ExpiringToken(None, datetime.now(timezone.utc)).is_valid())
        self.assertFalse(ExpiringToken("token", None).is_valid())

    def test_is_valid_treats_naive_expiration_as_utc(self):
        now_value = datetime(2030, 1, 1, tzinfo=timezone.utc)
        naive_expires_at = (now_value + timedelta(seconds=1)).replace(tzinfo=None)

        with patch("identity.domain.expiring_token.datetime") as datetime_mock:
            datetime_mock.now.return_value = now_value
            self.assertTrue(ExpiringToken("token", naive_expires_at).is_valid())

    def test_generate_password_hash_uses_the_injected_hasher(self):
        service = AuthenticationDomainService(FakeHasher())
        self.assertEqual(service.generate_password_hash("Abcdef1x"), "hash:Abcdef1x")

    def test_authenticate_uses_the_injected_hasher_verify(self):
        service = AuthenticationDomainService(FakeHasher())
        user = User(status=User.STATUS_ACTIVE, password_hash="hash:Abcdef1x")
        self.assertTrue(service.authenticate(user, "Abcdef1x"))
        self.assertFalse(service.authenticate(user, "OtraClave1"))

    def test_domain_does_not_import_werkzeug(self):
        from pathlib import Path

        import identity.domain.authentication_domain_service as module

        self.assertNotIn("werkzeug", Path(module.__file__).read_text(encoding="utf-8"))
if __name__ == "__main__":
    unittest.main()
