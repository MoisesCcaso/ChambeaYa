from profiles.application.dtos import UpdateCompanyDTO
from identity.api import User
from profiles.domain.company import Company
from profiles.domain.ruc import RUC
from shared.errors import DomainError, ForbiddenError, NotFoundError


class CompanyApplicationService:
    """Application service for the company profile lifecycle (SOLID-SRP)."""

    def __init__(self, company_repository=None, identity=None):
        self.company_repository = company_repository
        self.identity = identity

    def update_company(self, user_id, data):
        self._require_repositories()
        self._require_company_user(user_id)
        dto = UpdateCompanyDTO.from_dict(data)
        company = self.company_repository.find_company_by_user_id(user_id)
        if company is None:
            company = Company(user_id=user_id)

        if dto.ruc is not None:
            company.ruc = RUC(number=dto.ruc)

        if dto.legal_name is not None:
            company.legal_name = str(dto.legal_name).strip()
        if not company.legal_name:
            raise DomainError("La razón social es obligatoria")
        if not company.verify_ruc():
            raise DomainError("El RUC no es válido")
        return self.company_repository.save_company(company)

    update_profile = update_company

    def get_company_profile(self, user_id):
        self._require_repositories()
        self._require_company_user(user_id)
        return self.company_repository.find_company_by_user_id(user_id)

    get_profile = get_company_profile

    def _require_company_user(self, user_id):
        user = self.identity.find_user(user_id)
        if user is None:
            raise NotFoundError("Usuario no encontrado")
        if user.role != User.ROLE_COMPANY:
            raise ForbiddenError("El usuario no es empresa")
        if user.status != User.STATUS_ACTIVE:
            raise ForbiddenError("La cuenta no está activa")

        return user

    def _require_repositories(self):
        if self.company_repository is None:
            raise RuntimeError("CompanyApplicationService requires a company repository")
        if self.identity is None:
            raise RuntimeError("CompanyApplicationService requires the identity API")
