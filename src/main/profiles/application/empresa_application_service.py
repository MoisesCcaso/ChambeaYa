from profiles.application.dtos import ActualizarEmpresaDTO
from identity.api import User
from profiles.domain.empresa import Empresa
from profiles.domain.ruc import RUC
from shared.errors import DomainError, ForbiddenError, NotFoundError


class EmpresaApplicationService:
    """Servicio de aplicación especializado para el ciclo de vida de perfiles de empresas (SOLID-SRP)."""

    def __init__(self, empresa_repository=None, user_repository=None):
        self.empresa_repository = empresa_repository
        self.user_repository = user_repository

    def update_empresa(self, user_id, data):
        self._require_repositories()
        self._require_empresa_user(user_id)
        dto = ActualizarEmpresaDTO.from_dict(data)
        empresa = self.empresa_repository.find_empresa_by_user_id(user_id)
        if empresa is None:
            empresa = Empresa(user_id=user_id)

        if dto.ruc is not None:
            empresa.ruc = RUC(numero=dto.ruc)

        if dto.razon_social is not None:
            empresa.razon_social = str(dto.razon_social).strip()
        if not empresa.razon_social:
            raise DomainError("La razón social es obligatoria")
        if not empresa.verificar_ruc():
            raise DomainError("El RUC no es válido")
        return self.empresa_repository.save_empresa(empresa)

    update_profile = update_empresa

    def get_empresa_profile(self, user_id):
        self._require_repositories()
        self._require_empresa_user(user_id)
        return self.empresa_repository.find_empresa_by_user_id(user_id)

    get_profile = get_empresa_profile

    def _require_empresa_user(self, user_id):
        user = self.user_repository.find_by_id(user_id)
        if user is None:
            raise NotFoundError("Usuario no encontrado")
        if user.role != User.ROLE_COMPANY:
            raise ForbiddenError("El usuario no es empresa")
        if user.status != User.STATUS_ACTIVE:
            raise ForbiddenError("La cuenta no está activa")

        return user

    def _require_repositories(self):
        if self.empresa_repository is None:
            raise RuntimeError("EmpresaApplicationService requiere un repositorio de empresa")
        if self.user_repository is None:
            raise RuntimeError("EmpresaApplicationService requiere un repositorio de usuario")
