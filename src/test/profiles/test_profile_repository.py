"""I-05 - Tests for the SQLAlchemy profile repository with in-memory SQLite, no doubles.

Code under test:
- src/main/profiles/infrastructure/sqlalchemy_profile_repository.py
"""

import unittest

import pytest

from profiles.domain.company import Company
from profiles.domain.intern import Intern
from profiles.domain.ruc import RUC
from shared.database import db
from identity.infrastructure.models.user_model import UserModel
from profiles.infrastructure.sqlalchemy_profile_repository import SqlAlchemyProfileRepository


class TestProfileRepository(unittest.TestCase):
    """Persistence, read and mapping tests for SqlAlchemyProfileRepository."""

    @pytest.fixture(autouse=True)
    def _inject_context(self, app_context):
        self.app_context = app_context

    def setUp(self):
        self.repository = SqlAlchemyProfileRepository()

    def _create_user_in_db(self, email, role="practicante", status="activo"):
        user = UserModel(
            email=email,
            password_hash="hash_prueba",
            role=role,
            status=status,
        )
        db.session.add(user)
        db.session.commit()
        return user

    def test_save_and_reload_intern_profile_lists_and_flags(self):
        user = self._create_user_in_db("practicante1@test.local", role="practicante")
        intern = Intern(
            user_id=user.id,
            first_names="Lucía",
            last_names="Mendoza",
            dni="71234567",
            university_id_card="20210987",
            skills=["Python", "SQL", "Flask"],
            education=["UNSA - Ciencia de la Computación", "Inglés B2"],
            reputation_score=50.0,
            identity_verified=True,
        )

        saved = self.repository.save_intern(intern)

        self.assertIsNotNone(saved.id)
        self.assertEqual(saved.user_id, user.id)
        self.assertEqual(saved.first_names, "Lucía")
        self.assertEqual(saved.last_names, "Mendoza")
        self.assertEqual(saved.dni, "71234567")
        self.assertEqual(saved.university_id_card, "20210987")
        self.assertEqual(saved.skills, ["Python", "SQL", "Flask"])
        self.assertEqual(
            saved.education,
            ["UNSA - Ciencia de la Computación", "Inglés B2"],
        )
        self.assertEqual(saved.reputation_score, 50.0)
        self.assertTrue(saved.identity_verified)

        by_user = self.repository.find_intern_by_user_id(user.id)
        por_id = self.repository.find_intern_by_id(saved.id)

        for reloaded_intern in (by_user, por_id):
            self.assertIsNotNone(reloaded_intern)
            self.assertIsInstance(reloaded_intern, Intern)
            self.assertEqual(reloaded_intern.id, saved.id)
            self.assertEqual(reloaded_intern.user_id, user.id)
            self.assertEqual(reloaded_intern.first_names, "Lucía")
            self.assertEqual(reloaded_intern.last_names, "Mendoza")
            self.assertEqual(reloaded_intern.dni, "71234567")
            self.assertEqual(reloaded_intern.university_id_card, "20210987")
            self.assertEqual(reloaded_intern.skills, ["Python", "SQL", "Flask"])
            self.assertEqual(
                reloaded_intern.education,
                ["UNSA - Ciencia de la Computación", "Inglés B2"],
            )
            self.assertEqual(reloaded_intern.reputation_score, 50.0)
            self.assertTrue(reloaded_intern.identity_verified)

    def test_update_existing_intern_by_id_and_by_user_id(self):
        user = self._create_user_in_db("practicante2@test.local", role="practicante")
        inicial = self.repository.save_intern(
            Intern(
                user_id=user.id,
                first_names="Pedro",
                last_names="Ramos",
                skills=["Git"],
                education=["UNSA"],
                reputation_score=10.0,
                identity_verified=False,
            )
        )

        # Update when it comes with an existing id
        inicial.update_details(first_names="Pedro Alberto")
        inicial.skills = ["Git", "Docker"]
        inicial.identity_verified = True
        inicial.reputation_score = 40.0
        actualizado_por_id = self.repository.save_intern(inicial)
        self.assertEqual(actualizado_por_id.id, inicial.id)
        self.assertEqual(actualizado_por_id.first_names, "Pedro Alberto")
        self.assertEqual(actualizado_por_id.skills, ["Git", "Docker"])
        self.assertTrue(actualizado_por_id.identity_verified)

        # Update when id is None but the user_id already exists in the database
        without_id = Intern(
            id=None,
            user_id=user.id,
            first_names="Pedro Final",
            last_names="Ramos",
            skills=["Docker"],
            education=["UNSA", "Maestría"],
            reputation_score=15.0,
            identity_verified=False,
        )
        updated_through_user_id = self.repository.save_intern(without_id)
        self.assertEqual(updated_through_user_id.id, inicial.id)
        self.assertEqual(updated_through_user_id.first_names, "Pedro Final")
        self.assertEqual(updated_through_user_id.skills, ["Docker"])
        self.assertEqual(updated_through_user_id.education, ["UNSA", "Maestría"])
        self.assertFalse(updated_through_user_id.identity_verified)

    def test_save_and_reload_company_with_encapsulated_ruc(self):
        user = self._create_user_in_db("empresa1@test.local", role="empresa")
        company = Company(
            user_id=user.id,
            legal_name="Innovación Digital S.A.C.",
            ruc=RUC("20100070970"),
            verified=True,
        )

        saved = self.repository.save_company(company)

        self.assertIsNotNone(saved.id)
        self.assertEqual(saved.user_id, user.id)
        self.assertEqual(saved.legal_name, "Innovación Digital S.A.C.")
        self.assertIsInstance(saved.ruc, RUC)
        self.assertEqual(saved.ruc.number, "20100070970")
        self.assertTrue(saved.ruc.is_valid())
        self.assertTrue(saved.verified)

        reloaded = self.repository.find_company_by_user_id(user.id)
        self.assertIsNotNone(reloaded)
        self.assertIsInstance(reloaded, Company)
        self.assertEqual(reloaded.id, saved.id)
        self.assertEqual(reloaded.user_id, user.id)
        self.assertEqual(reloaded.legal_name, "Innovación Digital S.A.C.")
        self.assertIsInstance(reloaded.ruc, RUC)
        self.assertEqual(reloaded.ruc.number, "20100070970")
        self.assertTrue(reloaded.verified)

        # Update an existing company by id and by user_id
        reloaded.legal_name = "Innovación Digital Perú S.A.C."
        actualizada_id = self.repository.save_company(reloaded)
        self.assertEqual(actualizada_id.id, saved.id)
        self.assertEqual(actualizada_id.legal_name, "Innovación Digital Perú S.A.C.")

        updated_by_user_id = self.repository.save_company(
            Company(
                id=None,
                user_id=user.id,
                legal_name="Innovación Global S.A.C.",
                ruc=RUC("20100070988"),
                verified=False,
            )
        )
        self.assertEqual(updated_by_user_id.id, saved.id)
        self.assertEqual(updated_by_user_id.legal_name, "Innovación Global S.A.C.")
        self.assertEqual(updated_by_user_id.ruc.number, "20100070988")
        self.assertFalse(updated_by_user_id.verified)

    def test_missing_lookups_return_none(self):
        self.assertIsNone(self.repository.find_intern_by_user_id(99999))
        self.assertIsNone(self.repository.find_intern_by_id(99999))
        self.assertIsNone(self.repository.find_company_by_user_id(99999))

    def test_load_list_handles_empty_values_invalid_json_and_non_lists(self):
        self.assertEqual(self.repository._load_list(None), [])
        self.assertEqual(self.repository._load_list(""), [])
        self.assertEqual(self.repository._load_list("json-corrupto{"), [])
        self.assertEqual(self.repository._load_list('{"clave": "valor"}'), [])
        self.assertEqual(self.repository._load_list('["Python", "SQL"]'), ["Python", "SQL"])

    def test_segregated_interface_implements_both_contracts(self):
        from profiles.domain.i_intern_repository import IInternRepository
        from profiles.domain.i_company_repository import ICompanyRepository
        from profiles.domain.i_profile_repository import IProfileRepository

        self.assertIsInstance(self.repository, IInternRepository)
        self.assertIsInstance(self.repository, ICompanyRepository)
        self.assertIsInstance(self.repository, IProfileRepository)
        self.assertTrue(issubclass(IProfileRepository, IInternRepository))
        self.assertTrue(issubclass(IProfileRepository, ICompanyRepository))


if __name__ == "__main__":
    unittest.main()
