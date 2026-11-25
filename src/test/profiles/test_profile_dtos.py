"""Unit tests for the profiles Parameter Objects (DTOs) (Issue #180)."""

import unittest
from unittest.mock import create_autospec

from profiles.application.dtos import UpdateCompanyDTO, UpdateInternDTO
from profiles.application.company_application_service import CompanyApplicationService
from profiles.application.intern_application_service import InternApplicationService
from identity.domain.i_user_repository import IUserRepository
from identity.domain.user import User
from profiles.domain.i_company_repository import ICompanyRepository
from profiles.domain.i_intern_repository import IInternRepository
from profiles.domain.intern import Intern


class TestProfileParameterObjectsDTO(unittest.TestCase):
    """Unit tests for UpdateInternDTO and UpdateCompanyDTO."""

    def setUp(self):
        self.intern_repo = create_autospec(IInternRepository, instance=True, spec_set=True)
        self.company_repo = create_autospec(ICompanyRepository, instance=True, spec_set=True)
        self.user_repo = create_autospec(IUserRepository, instance=True, spec_set=True)
        self.intern_service = InternApplicationService(
            intern_repository=self.intern_repo,
            user_repository=self.user_repo,
        )
        self.company_service = CompanyApplicationService(
            company_repository=self.company_repo,
            user_repository=self.user_repo,
        )

    def test_update_intern_accepts_typed_dto(self):
        self.user_repo.find_by_id.return_value = User(
            id=10,
            email="alumno@unsa.edu.pe",
            password_hash="h",
            role=User.ROLE_INTERN,
            status=User.STATUS_ACTIVE,
        )
        self.intern_repo.find_intern_by_user_id.return_value = None
        self.intern_repo.save_intern.side_effect = lambda p: p

        dto = UpdateInternDTO(
            first_names="Omar",
            last_names="Rivera",
            dni="12345678",
            university_id_card="20210001",
            skills=["Python", "Clean Architecture"],
            education=["UNSA"],
        )
        intern = self.intern_service.update_intern(10, dto)

        self.assertEqual(intern.first_names, "Omar")
        self.assertEqual(intern.last_names, "Rivera")
        self.assertTrue(intern.identity_verified)
        self.assertEqual(intern.skills, ["Python", "Clean Architecture"])

    def test_update_intern_dto_tells_omitted_fields_apart(self):
        existing = Intern(
            id=1,
            user_id=10,
            first_names="Omar",
            last_names="Rivera",
            dni="12345678",
            identity_verified=True,
        )
        self.user_repo.find_by_id.return_value = User(
            id=10,
            email="alumno@unsa.edu.pe",
            password_hash="h",
            role=User.ROLE_INTERN,
            status=User.STATUS_ACTIVE,
        )
        self.intern_repo.find_intern_by_user_id.return_value = existing
        self.intern_repo.save_intern.side_effect = lambda p: p

        dto = UpdateInternDTO.from_dict({"nombres": "Omar Joaquin", "apellidos": "Rivera"})
        updated_certificate = self.intern_service.update_intern(10, dto)

        self.assertEqual(updated_certificate.first_names, "Omar Joaquin")
        self.assertEqual(updated_certificate.dni, "12345678")
        self.assertTrue(updated_certificate.identity_verified)

    def test_update_company_accepts_typed_dto(self):
        self.user_repo.find_by_id.return_value = User(
            id=20,
            email="rrhh@empresa.pe",
            password_hash="h",
            role=User.ROLE_COMPANY,
            status=User.STATUS_ACTIVE,
        )
        self.company_repo.find_company_by_user_id.return_value = None
        self.company_repo.save_company.side_effect = lambda e: e

        dto = UpdateCompanyDTO(legal_name="Tech Peru SAC", ruc="20100070970")
        company = self.company_service.update_company(20, dto)

        self.assertEqual(company.legal_name, "Tech Peru SAC")
        self.assertEqual(company.ruc.number, "20100070970")
        self.assertTrue(company.verified)


if __name__ == "__main__":
    unittest.main()
