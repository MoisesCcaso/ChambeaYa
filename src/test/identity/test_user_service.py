"""I-03 - Tests for the user application service (autospec doubles).

Code under test: identity/application/user_application_service.py
"""
import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import create_autospec, patch

from identity.application.email_delivery_error import EmailDeliveryError
from identity.application.user_application_service import UserApplicationService
from identity.domain.authentication_domain_service import AuthenticationDomainService
from identity.domain.i_auth_email_sender import IAuthEmailSender
from identity.domain.i_user_repository import IUserRepository
from identity.domain.user import User
from werkzeug.security import check_password_hash
from identity.infrastructure.werkzeug_password_hasher import WerkzeugPasswordHasher


class TestUserService(unittest.TestCase):
    def setUp(self):
        self.repository = create_autospec(IUserRepository, instance=True, spec_set=True)
        self.sender = create_autospec(IAuthEmailSender, instance=True, spec_set=True)
        self.auth = AuthenticationDomainService(WerkzeugPasswordHasher())
        self.service = UserApplicationService(
            user_repository=self.repository,
            authentication_domain_service=self.auth,
            email_sender=self.sender,
        )
        self.now_value = datetime(2030, 1, 1, tzinfo=timezone.utc)
        self._datetime_patcher = patch("identity.domain.authentication_domain_service.datetime")
        self.datetime_mock = self._datetime_patcher.start()
        self.datetime_mock.now.return_value = self.now_value

    def tearDown(self):
        self._datetime_patcher.stop()

    def test_registration_normalizes_email_saves_pending_user_and_sends_activation(self):
        self.repository.find_by_email.return_value = None
        self.repository.save.side_effect = lambda user: user

        result = self.service.register_user(
            "  Ana.PEREZ@Example.COM ", "Abcdefg1", "Abcdefg1", User.ROLE_INTERN,
        )

        self.assertEqual(result.email, "ana.perez@example.com")
        self.assertEqual(result.status, User.STATUS_PENDING)
        self.assertIsNotNone(result.activation_token)
        self.assertEqual(
            result.activation_token_expires_at, self.now_value + timedelta(hours=48)
        )
        self.repository.find_by_email.assert_called_once_with("ana.perez@example.com")
        self.repository.save.assert_called_once()
        self.sender.send_activation.assert_called_once_with(
            "ana.perez@example.com", result.activation_token
        )

    def test_registration_with_duplicate_email_neither_saves_nor_sends(self):
        existing = User(
            email="ana@test.local", password_hash="hash", role=User.ROLE_COMPANY
        )
        self.repository.find_by_email.return_value = existing

        with self.assertRaisesRegex(ValueError, "ya está registrado"):
            self.service.register_user(
                "ana@test.local", "Abcdefg1", "Abcdefg1", User.ROLE_COMPANY
            )

        self.repository.save.assert_not_called()
        self.sender.send_activation.assert_not_called()

    def test_registration_with_mismatched_passwords_raises(self):
        self.repository.find_by_email.return_value = None

        with self.assertRaisesRegex(ValueError, "no coinciden"):
            self.service.register_user(
                "ana@test.local", "Abcdefg1", "OtraClave1", User.ROLE_INTERN
            )

        self.repository.save.assert_not_called()
        self.sender.send_activation.assert_not_called()

    def test_registration_email_sender_raises_email_delivery_error(self):
        self.repository.find_by_email.return_value = None
        self.repository.save.side_effect = lambda user: user
        self.sender.send_activation.side_effect = EmailDeliveryError("fallo smtp")

        with self.assertRaises(EmailDeliveryError):
            self.service.register_user(
                "ana@test.local", "Abcdefg1", "Abcdefg1", User.ROLE_INTERN
            )

        self.repository.save.assert_called_once()
        self.sender.send_activation.assert_called_once()

    def test_authenticate_returns_user_with_valid_credentials(self):
        password = "Abcdefg1"
        real_hash = self.auth.generate_password_hash(password)
        user = User(
            email="ana@test.local",
            password_hash=real_hash,
            role=User.ROLE_INTERN,
            status=User.STATUS_ACTIVE,
        )
        self.repository.find_by_email.return_value = user

        result = self.service.authenticate("ana@test.local", password)

        self.assertIs(result, user)
        self.repository.find_by_email.assert_called_once_with("ana@test.local")
        self.assertTrue(check_password_hash(user.password_hash, password))

    def test_authenticate_rejects_wrong_password(self):
        password = "Abcdefg1"
        real_hash = self.auth.generate_password_hash(password)
        user = User(
            email="ana@test.local",
            password_hash=real_hash,
            role=User.ROLE_INTERN,
            status=User.STATUS_ACTIVE,
        )
        self.repository.find_by_email.return_value = user

        with self.assertRaisesRegex(ValueError, "Credenciales inválidas"):
            self.service.authenticate("ana@test.local", "OtraClave1")

    def test_authenticate_missing_user_raises(self):
        self.repository.find_by_email.return_value = None

        with self.assertRaisesRegex(ValueError, "Credenciales inválidas"):
            self.service.authenticate("no-existe@test.local", "Abcdefg1")

    def test_recovery_missing_user_neither_saves_nor_sends(self):
        self.repository.find_by_email.return_value = None

        result = self.service.recover_password("no-existe@test.local")

        self.assertIsNone(result)
        self.repository.save.assert_not_called()
        self.sender.send_password_reset.assert_not_called()

    def test_recovery_existing_user_gets_two_hour_token_saved_and_sent(self):
        user = User(
            email="ana@test.local",
            password_hash="hash",
            role=User.ROLE_INTERN,
        )
        self.repository.find_by_email.return_value = user
        self.repository.save.side_effect = lambda u: u

        result = self.service.recover_password("ana@test.local")

        self.assertIs(result, user)
        self.assertIsNotNone(user.password_reset_token)
        self.assertEqual(
            user.password_reset_expires_at, self.now_value + timedelta(hours=2)
        )
        self.repository.save.assert_called_once_with(user)
        self.sender.send_password_reset.assert_called_once_with(
            "ana@test.local", user.password_reset_token
        )

    def test_recovery_looks_up_normalized_email(self):
        self.repository.find_by_email.return_value = None
        self.service.recover_password("  ANA@Example.COM ")
        self.repository.find_by_email.assert_called_once_with("ana@example.com")

    def test_resend_activation_missing_user_returns_none(self):
        self.repository.find_by_email.return_value = None

        result = self.service.resend_activation("no-existe@test.local")

        self.assertIsNone(result)
        self.repository.save.assert_not_called()
        self.sender.send_activation.assert_not_called()

    def test_resend_activation_active_user_returns_none(self):
        user = User(
            email="ana@test.local",
            password_hash="hash",
            role=User.ROLE_INTERN,
            status=User.STATUS_ACTIVE,
        )
        self.repository.find_by_email.return_value = user

        result = self.service.resend_activation("ana@test.local")

        self.assertIsNone(result)
        self.repository.save.assert_not_called()
        self.sender.send_activation.assert_not_called()

    def test_resend_activation_pending_user_sends_new_token(self):
        user = User(
            email="ana@test.local",
            password_hash="hash",
            role=User.ROLE_INTERN,
            status=User.STATUS_PENDING,
        )
        self.repository.find_by_email.return_value = user
        self.repository.save.side_effect = lambda u: u

        result = self.service.resend_activation("ana@test.local")

        self.assertIs(result, user)
        self.assertIsNotNone(user.activation_token)
        self.assertEqual(
            user.activation_token_expires_at, self.now_value + timedelta(hours=48)
        )
        self.repository.save.assert_called_once_with(user)
        self.sender.send_activation.assert_called_once_with(
            "ana@test.local", user.activation_token
        )

    def test_activate_account_with_invalid_token_raises(self):
        self.repository.find_by_activation_token.return_value = None

        with self.assertRaisesRegex(ValueError, "Token de activación inválido"):
            self.service.activate_account("token-inexistente")

        self.repository.save.assert_not_called()

    def test_activate_account_with_expired_token_raises(self):
        user = User(
            email="ana@test.local",
            password_hash="hash",
            role=User.ROLE_INTERN,
            status=User.STATUS_PENDING,
            activation_token="token-valido",
            activation_token_expires_at=datetime(2020, 1, 1, tzinfo=timezone.utc),
        )
        self.repository.find_by_activation_token.return_value = user

        with self.assertRaisesRegex(ValueError, "Token de activación expirado"):
            self.service.activate_account("token-valido")

        self.repository.save.assert_not_called()

    def test_activate_account_with_valid_token_activates_and_saves(self):
        user = User(
            email="ana@test.local",
            password_hash="hash",
            role=User.ROLE_INTERN,
            status=User.STATUS_PENDING,
            activation_token="token-valido",
            activation_token_expires_at=self.now_value + timedelta(hours=1),
        )
        self.repository.find_by_activation_token.return_value = user
        self.repository.save.side_effect = lambda u: u

        result = self.service.activate_account("token-valido")

        self.assertIs(result, user)
        self.assertEqual(user.status, User.STATUS_ACTIVE)
        self.assertIsNone(user.activation_token)
        self.repository.save.assert_called_once_with(user)

    def test_reset_password_with_missing_token_raises(self):
        self.repository.find_by_password_reset_token.return_value = None

        with self.assertRaisesRegex(ValueError, "Token de recuperación inválido"):
            self.service.reset_password("token-inexistente", "NuevaClave1")

        self.repository.save.assert_not_called()

    def test_reset_password_with_expired_token_raises(self):
        user = User(
            email="ana@test.local",
            password_hash="hash",
            role=User.ROLE_INTERN,
            status=User.STATUS_ACTIVE,
            password_reset_token="token-valido",
            password_reset_expires_at=datetime(2020, 1, 1, tzinfo=timezone.utc),
        )
        self.repository.find_by_password_reset_token.return_value = user

        with self.assertRaisesRegex(ValueError, "Token de recuperación expirado"):
            self.service.reset_password("token-valido", "NuevaClave1")

        self.repository.save.assert_not_called()

    def test_reset_password_with_valid_token_updates_and_saves(self):
        user = User(
            email="ana@test.local",
            password_hash="hash-viejo",
            role=User.ROLE_INTERN,
            status=User.STATUS_ACTIVE,
            password_reset_token="token-valido",
            password_reset_expires_at=self.now_value + timedelta(hours=2),
        )
        self.repository.find_by_password_reset_token.return_value = user
        self.repository.save.side_effect = lambda u: u

        result = self.service.reset_password("token-valido", "NuevaClave1")

        self.assertIs(result, user)
        self.assertNotEqual(user.password_hash, "hash-viejo")
        self.assertTrue(check_password_hash(user.password_hash, "NuevaClave1"))
        self.assertIsNone(user.password_reset_token)
        self.repository.save.assert_called_once_with(user)

    def test_find_by_id_delegates_to_the_repository(self):
        user = User(id=7, email="ana@test.local", password_hash="hash")
        self.repository.find_by_id.return_value = user

        result = self.service.find_by_id(7)

        self.assertIs(result, user)
        self.repository.find_by_id.assert_called_once_with(7)

    def test_without_repository_raises_runtime_error(self):
        service = UserApplicationService()
        with self.assertRaises(RuntimeError):
            service.register_user(
                "a@b.c", "Abcdefg1", "Abcdefg1", User.ROLE_INTERN
            )

    def test_registration_without_email_sender_raises_runtime_error(self):
        service = UserApplicationService(user_repository=self.repository)
        self.repository.find_by_email.return_value = None

        with self.assertRaises(RuntimeError):
            service.register_user(
                "a@b.c", "Abcdefg1", "Abcdefg1", User.ROLE_INTERN
            )

    def test_normalize_email_returns_normalized_valid_email(self):
        result = self.service._normalize_email("  Ana.PEREZ@Example.COM ")
        self.assertEqual(result, "ana.perez@example.com")

    def test_normalize_email_empty_raises(self):
        with self.assertRaisesRegex(ValueError, "El email es obligatorio"):
            self.service._normalize_email("")

    def test_normalize_email_invalid_raises(self):
        with self.assertRaisesRegex(ValueError, "El email no es válido"):
            self.service._normalize_email("no-es-un-email")


if __name__ == "__main__":
    unittest.main()
