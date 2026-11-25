from profiles.application.dtos import UpdateInternDTO, UNSET
from identity.api import User
from profiles.domain.intern import Intern
from shared.errors import ForbiddenError, NotFoundError


class InternApplicationService:
    """Application service for the intern profile lifecycle (SOLID-SRP)."""

    def __init__(self, intern_repository=None, user_repository=None):
        self.intern_repository = intern_repository
        self.user_repository = user_repository

    def get_intern_profile(self, user_id):
        self._require_repositories()
        self._require_intern_user(user_id)
        return self.intern_repository.find_intern_by_user_id(user_id)

    get_profile = get_intern_profile

    def update_intern(self, user_id, data):
        self._require_repositories()
        self._require_intern_user(user_id)
        dto = UpdateInternDTO.from_dict(data)

        intern = self.intern_repository.find_intern_by_user_id(user_id)
        if intern is None:
            intern = Intern(user_id=user_id)

        intern.update_details(
            first_names=dto.first_names,
            last_names=dto.last_names,
        )

        identity_updated = (
            dto.dni is not UNSET or dto.university_id_card is not UNSET
        )
        if dto.dni is not UNSET:
            intern.dni = self._optional_text(dto.dni)
        if dto.university_id_card is not UNSET:
            intern.university_id_card = self._optional_text(
                dto.university_id_card
            )
        if dto.skills is not UNSET:
            intern.replace_skills(dto.skills or [])
        if dto.education is not UNSET:
            intern.replace_education(dto.education or [])

        if identity_updated:
            if intern.dni or intern.university_id_card:
                intern.verify_identity()
            else:
                intern.revoke_identity_verification()

        return self.intern_repository.save_intern(intern)

    update_profile = update_intern

    def add_skill(self, user_id, skill):
        self._require_repositories()
        intern = self._get_or_create_intern(user_id)
        intern.add_skill(skill)
        return self.intern_repository.save_intern(intern)

    def add_education(self, user_id, education_entry):
        self._require_repositories()
        intern = self._get_or_create_intern(user_id)
        intern.add_education(education_entry)
        return self.intern_repository.save_intern(intern)

    def register_identity(self, user_id, dni=None, university_id_card=None):
        self._require_repositories()
        intern = self._get_or_create_intern(user_id)
        intern.update_details(dni=dni, university_id_card=university_id_card)
        intern.verify_identity()
        return self.intern_repository.save_intern(intern)

    def verify_profile(self, user_id):
        self._require_repositories()
        intern = self.intern_repository.find_intern_by_user_id(user_id)
        if intern is None:
            raise ForbiddenError("Perfil de practicante no encontrado")

        return intern.identity_verified

    def get_reputation_score(self, user_id):
        self._require_repositories()
        intern = self.intern_repository.find_intern_by_user_id(user_id)
        if intern is None:
            return 0.0

        return intern.reputation_score

    def _get_or_create_intern(self, user_id):
        self._require_intern_user(user_id)
        intern = self.intern_repository.find_intern_by_user_id(user_id)
        if intern is None:
            intern = Intern(user_id=user_id)

        return intern

    def _require_intern_user(self, user_id):
        user = self.user_repository.find_by_id(user_id)
        if user is None:
            raise NotFoundError("Usuario no encontrado")
        if user.role != User.ROLE_INTERN:
            raise ForbiddenError("El usuario no es practicante")
        if user.status != User.STATUS_ACTIVE:
            raise ForbiddenError("La cuenta no está activa")

        return user

    def _require_repositories(self):
        if self.intern_repository is None:
            raise RuntimeError("InternApplicationService requires an intern repository")
        if self.user_repository is None:
            raise RuntimeError("InternApplicationService requires a user repository")

    def _optional_text(self, value):
        if value is None:
            return None
        normalized = str(value).strip()
        return normalized or None
