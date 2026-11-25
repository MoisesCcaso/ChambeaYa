"""I-06 - Unit tests for the profile application services with doubles (autospec).

Code under test:
- src/main/profiles/application/intern_application_service.py
- src/main/profiles/application/company_application_service.py
"""

import unittest
from unittest.mock import create_autospec

from profiles.application.company_application_service import CompanyApplicationService
from profiles.application.intern_application_service import InternApplicationService
from identity.api import IdentityApi
from identity.domain.user import User
from profiles.domain.company import Company
from profiles.domain.i_company_repository import ICompanyRepository
from profiles.domain.i_profile_repository import IProfileRepository
from profiles.domain.i_intern_repository import IInternRepository
from profiles.domain.intern import Intern
from profiles.domain.ruc import RUC


class TestProfileService(unittest.TestCase):
    """Intern and Company services with the combined IProfileRepository, as wired by dependencies.py."""

    def setUp(self):
        self.profile_repository = create_autospec(
            IProfileRepository, instance=True, spec_set=True
        )
        self.identity = create_autospec(
            IdentityApi, instance=True, spec_set=True
        )
        self.intern_service = InternApplicationService(
            intern_repository=self.profile_repository,
            identity=self.identity,
        )
        self.company_service = CompanyApplicationService(
            company_repository=self.profile_repository,
            identity=self.identity,
        )

    def _active_intern_user(self, user_id=10):
        return User(
            id=user_id,
            email="practicante@test.local",
            password_hash="hash",
            role=User.ROLE_INTERN,
            status=User.STATUS_ACTIVE,
        )

    def _active_company_user(self, user_id=20):
        return User(
            id=user_id,
            email="empresa@test.local",
            password_hash="hash",
            role=User.ROLE_COMPANY,
            status=User.STATUS_ACTIVE,
        )

    def test_update_active_intern_creates_or_updates_verifies_identity_and_saves(self):
        user = self._active_intern_user(user_id=10)
        self.identity.find_user.return_value = user
        self.profile_repository.find_intern_by_user_id.return_value = None
        self.profile_repository.save_intern.side_effect = lambda p: p

        details = {
            "nombres": "Ana",
            "apellidos": "Torres",
            "dni": "  71234567  ",
            "carnet_universitario": "  20214567  ",
            "habilidades": [" Python ", "SQL", "Python"],
            "formacion_educativa": [" UNSA ", "Inglés"],
        }

        result = self.intern_service.update_intern(10, details)

        self.identity.find_user.assert_called_once_with(10)
        self.profile_repository.find_intern_by_user_id.assert_called_once_with(10)
        self.profile_repository.save_intern.assert_called_once()

        saved_intern = self.profile_repository.save_intern.call_args[0][0]
        self.assertIs(result, saved_intern)
        self.assertEqual(saved_intern.user_id, 10)
        self.assertEqual(saved_intern.first_names, "Ana")
        self.assertEqual(saved_intern.last_names, "Torres")
        self.assertEqual(saved_intern.dni, "71234567")
        self.assertEqual(saved_intern.university_id_card, "20214567")
        self.assertEqual(saved_intern.skills, ["Python", "SQL"])
        self.assertEqual(saved_intern.education, ["UNSA", "Inglés"])
        self.assertTrue(saved_intern.identity_verified)
        # 2 skills (10) + 2 education entries (10) + verified identity (25) = 45.0
        self.assertEqual(saved_intern.reputation_score, 45.0)

    def test_update_existing_intern_clears_identity_when_sent_empty(self):
        user = self._active_intern_user(user_id=10)
        existing = Intern(
            id=5,
            user_id=10,
            first_names="Ana",
            last_names="Torres",
            dni="71234567",
            identity_verified=True,
            reputation_score=25.0,
        )
        self.identity.find_user.return_value = user
        self.profile_repository.find_intern_by_user_id.return_value = existing
        self.profile_repository.save_intern.side_effect = lambda p: p

        result = self.intern_service.update_intern(
            10, {"dni": "   ", "carnet_universitario": None}
        )

        self.assertIs(result, existing)
        self.assertIsNone(existing.dni)
        self.assertIsNone(existing.university_id_card)
        self.assertFalse(existing.identity_verified)
        self.assertEqual(existing.reputation_score, 0.0)
        self.profile_repository.save_intern.assert_called_once_with(existing)

    def test_update_intern_rejects_missing_user_before_saving(self):
        self.identity.find_user.return_value = None

        with self.assertRaisesRegex(ValueError, "Usuario no encontrado"):
            self.intern_service.update_intern(99, {"nombres": "Ana"})

        self.identity.find_user.assert_called_once_with(99)
        self.profile_repository.find_intern_by_user_id.assert_not_called()
        self.profile_repository.save_intern.assert_not_called()

    def test_update_intern_rejects_inactive_user_before_saving(self):
        inactive_user = User(
            id=10,
            email="pendiente@test.local",
            password_hash="hash",
            role=User.ROLE_INTERN,
            status=User.STATUS_PENDING,
        )
        self.identity.find_user.return_value = inactive_user

        with self.assertRaisesRegex(ValueError, "La cuenta no está activa"):
            self.intern_service.update_intern(10, {"nombres": "Ana"})

        self.identity.find_user.assert_called_once_with(10)
        self.profile_repository.find_intern_by_user_id.assert_not_called()
        self.profile_repository.save_intern.assert_not_called()

    def test_update_intern_rejects_company_user_before_saving(self):
        company_user = self._active_company_user(user_id=20)
        self.identity.find_user.return_value = company_user

        with self.assertRaisesRegex(ValueError, "El usuario no es practicante"):
            self.intern_service.update_intern(20, {"nombres": "Ana"})

        self.identity.find_user.assert_called_once_with(20)
        self.profile_repository.find_intern_by_user_id.assert_not_called()
        self.profile_repository.save_intern.assert_not_called()

    def test_get_intern_profile_and_skill_education_identity_operations(self):
        user = self._active_intern_user(user_id=10)
        self.identity.find_user.return_value = user
        self.profile_repository.find_intern_by_user_id.return_value = None
        self.profile_repository.save_intern.side_effect = lambda p: p

        self.assertIsNone(self.intern_service.get_intern_profile(10))

        with_skill = self.intern_service.add_skill(10, "  Python  ")
        self.assertEqual(with_skill.skills, ["Python"])
        self.assertEqual(with_skill.reputation_score, 5.0)

        self.profile_repository.find_intern_by_user_id.return_value = with_skill
        with_education = self.intern_service.add_education(10, "  UNSA  ")
        self.assertEqual(with_education.education, ["UNSA"])
        self.assertEqual(with_education.reputation_score, 10.0)

        with_identity = self.intern_service.register_identity(
            10, dni="71234567", university_id_card="20210001"
        )
        self.assertTrue(with_identity.identity_verified)
        self.assertEqual(with_identity.reputation_score, 35.0)

    def test_update_and_get_company_profile_and_company_guards(self):
        company_user = self._active_company_user(user_id=20)
        self.identity.find_user.return_value = company_user
        self.profile_repository.find_company_by_user_id.return_value = None
        self.profile_repository.save_company.side_effect = lambda e: e

        # Valid company save
        saved_company = self.company_service.update_company(
            20, {"razon_social": "  Acme S.A.C.  ", "ruc": "20100070970"}
        )
        self.assertEqual(saved_company.user_id, 20)
        self.assertEqual(saved_company.legal_name, "Acme S.A.C.")
        self.assertIsInstance(saved_company.ruc, RUC)
        self.assertTrue(saved_company.verified)
        self.profile_repository.save_company.assert_called_once_with(saved_company)

        self.profile_repository.find_company_by_user_id.return_value = saved_company
        self.assertIs(self.company_service.get_company_profile(20), saved_company)

        # Update an existing company
        existing = Company(
            id=3, user_id=20, legal_name="Anterior S.A.C.", ruc=RUC("20100070970")
        )
        self.profile_repository.find_company_by_user_id.return_value = existing
        updated = self.company_service.update_company(
            20, {"razon_social": "Nueva Razón S.A.C."}
        )
        self.assertIs(updated, existing)
        self.assertEqual(updated.legal_name, "Nueva Razón S.A.C.")
        self.assertTrue(updated.verified)

        # Empty legal name
        with self.assertRaisesRegex(ValueError, "La razón social es obligatoria"):
            self.company_service.update_company(20, {"razon_social": "   ", "ruc": "20100070970"})

        # Invalid RUC
        with self.assertRaisesRegex(ValueError, "El RUC no es válido"):
            self.company_service.update_company(
                20, {"razon_social": "Acme S.A.C.", "ruc": "20100070975"}
            )

        # Company user guards: missing, intern role, inactive
        self.identity.find_user.return_value = None
        with self.assertRaisesRegex(ValueError, "Usuario no encontrado"):
            self.company_service.update_company(99, {"razon_social": "X", "ruc": "20100070970"})

        self.identity.find_user.return_value = self._active_intern_user(10)
        with self.assertRaisesRegex(ValueError, "El usuario no es empresa"):
            self.company_service.update_company(10, {"razon_social": "X", "ruc": "20100070970"})

        self.identity.find_user.return_value = User(
            id=20,
            email="emp@test.local",
            password_hash="h",
            role=User.ROLE_COMPANY,
            status=User.STATUS_PENDING,
        )
        with self.assertRaisesRegex(ValueError, "La cuenta no está activa"):
            self.company_service.update_company(20, {"razon_social": "X", "ruc": "20100070970"})

    def test_verify_profile_and_get_reputation_score(self):
        self.profile_repository.find_intern_by_user_id.return_value = None
        with self.assertRaisesRegex(ValueError, "Perfil de practicante no encontrado"):
            self.intern_service.verify_profile(10)
        self.assertEqual(self.intern_service.get_reputation_score(10), 0.0)

        intern = Intern(
            user_id=10, identity_verified=True, reputation_score=65.0
        )
        self.profile_repository.find_intern_by_user_id.return_value = intern
        self.assertTrue(self.intern_service.verify_profile(10))
        self.assertEqual(self.intern_service.get_reputation_score(10), 65.0)

    def test_requires_configured_repositories(self):
        without_profile_repo = InternApplicationService(
            intern_repository=None, identity=self.identity
        )
        with self.assertRaisesRegex(
            RuntimeError, "requires an intern repository"
        ):
            without_profile_repo.get_intern_profile(10)

        without_identity = InternApplicationService(
            intern_repository=self.profile_repository, identity=None
        )
        with self.assertRaisesRegex(
            RuntimeError, "requires the identity API"
        ):
            without_identity.get_intern_profile(10)

        without_company_repo = CompanyApplicationService(
            company_repository=None, identity=self.identity
        )
        with self.assertRaisesRegex(
            RuntimeError, "requires a company repository"
        ):
            without_company_repo.get_company_profile(20)


class TestInternApplicationService(unittest.TestCase):
    """Isolated tests for InternApplicationService using the segregated IInternRepository."""

    def setUp(self):
        self.intern_repo = create_autospec(IInternRepository, instance=True, spec_set=True)
        self.user_repo = create_autospec(IdentityApi, instance=True, spec_set=True)
        self.service = InternApplicationService(
            intern_repository=self.intern_repo,
            identity=self.user_repo,
        )

    def test_updates_skills_and_reputation_with_segregated_repo(self):
        user = User(id=22, email="student@test.pe", password_hash="hash", role=User.ROLE_INTERN, status=User.STATUS_ACTIVE)
        self.user_repo.find_user.return_value = user
        self.intern_repo.find_intern_by_user_id.return_value = None
        self.intern_repo.save_intern.side_effect = lambda p: p

        intern = self.service.add_skill(22, "FastAPI")
        self.assertIn("FastAPI", intern.skills)
        self.intern_repo.save_intern.assert_called_once()

    def test_requires_repositories(self):
        without_repo = InternApplicationService(intern_repository=None, identity=self.user_repo)
        with self.assertRaises(RuntimeError):
            without_repo.get_profile(22)


class TestCompanyApplicationService(unittest.TestCase):
    """Isolated tests for CompanyApplicationService using the segregated ICompanyRepository."""

    def setUp(self):
        self.company_repo = create_autospec(ICompanyRepository, instance=True, spec_set=True)
        self.user_repo = create_autospec(IdentityApi, instance=True, spec_set=True)
        self.service = CompanyApplicationService(
            company_repository=self.company_repo,
            identity=self.user_repo,
        )

    def test_updates_company_with_segregated_repo(self):
        user = User(id=33, email="empresa@test.pe", password_hash="hash", role=User.ROLE_COMPANY, status=User.STATUS_ACTIVE)
        self.user_repo.find_user.return_value = user
        self.company_repo.find_company_by_user_id.return_value = None
        self.company_repo.save_company.side_effect = lambda e: e

        company = self.service.update_company(33, {"razon_social": "Acme SAC", "ruc": "20100070988"})
        self.assertEqual(company.legal_name, "Acme SAC")
        self.company_repo.save_company.assert_called_once()

    def test_requires_repositories(self):
        without_repo = CompanyApplicationService(company_repository=None, identity=self.user_repo)
        with self.assertRaises(RuntimeError):
            without_repo.get_profile(33)


if __name__ == "__main__":
    unittest.main()
