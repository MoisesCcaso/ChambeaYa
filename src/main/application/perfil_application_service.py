#!/usr/bin/python
# -*- coding: utf-8 -*-

from application.empresa_application_service import EmpresaApplicationService
from application.practicante_application_service import PracticanteApplicationService


class PerfilApplicationService:
    """Fachada unificada de perfiles que delega a PracticanteApplicationService y EmpresaApplicationService (SOLID-SRP)."""

    def __init__(self, perfil_repository=None, usuario_repository=None,
                 practicante_service=None, empresa_service=None):
        self.perfil_repository = perfil_repository
        self.usuario_repository = usuario_repository
        self.practicante_service = practicante_service or (
            PracticanteApplicationService(perfil_repository, usuario_repository)
            if perfil_repository and usuario_repository else None
        )
        self.empresa_service = empresa_service or (
            EmpresaApplicationService(perfil_repository, usuario_repository)
            if perfil_repository and usuario_repository else None
        )

    def get_practicante_profile(self, usuario_id):
        self._require_repositories()
        return self._get_practicante_service().get_practicante_profile(usuario_id)

    def update_practicante(self, usuario_id, data):
        self._require_repositories()
        return self._get_practicante_service().update_practicante(usuario_id, data)

    def add_habilidad(self, usuario_id, habilidad):
        self._require_repositories()
        return self._get_practicante_service().add_habilidad(usuario_id, habilidad)

    def add_formacion(self, usuario_id, formacion):
        self._require_repositories()
        return self._get_practicante_service().add_formacion(usuario_id, formacion)

    def register_identity(self, usuario_id, dni=None, carnet_universitario=None):
        self._require_repositories()
        return self._get_practicante_service().register_identity(
            usuario_id, dni=dni, carnet_universitario=carnet_universitario
        )

    def update_empresa(self, usuario_id, data):
        self._require_repositories()
        return self._get_empresa_service().update_empresa(usuario_id, data)

    def get_empresa_profile(self, usuario_id):
        self._require_repositories()
        return self._get_empresa_service().get_empresa_profile(usuario_id)

    def verify_profile(self, usuario_id):
        self._require_repositories()
        return self._get_practicante_service().verify_profile(usuario_id)

    def get_reputation_score(self, usuario_id):
        self._require_repositories()
        return self._get_practicante_service().get_reputation_score(usuario_id)

    def _get_practicante_service(self):
        if self.practicante_service is None:
            self.practicante_service = PracticanteApplicationService(
                self.perfil_repository, self.usuario_repository
            )
        return self.practicante_service

    def _get_empresa_service(self):
        if self.empresa_service is None:
            self.empresa_service = EmpresaApplicationService(
                self.perfil_repository, self.usuario_repository
            )
        return self.empresa_service

    def _require_repositories(self):
        if self.perfil_repository is None:
            raise RuntimeError("PerfilApplicationService requiere un repositorio de perfil")
        if self.usuario_repository is None:
            raise RuntimeError("PerfilApplicationService requiere un repositorio de usuario")

