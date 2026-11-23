#!/usr/bin/python
# -*- coding: utf-8 -*-

from application.dtos import ActualizarEmpresaDTO
from domain.auth.usuario import Usuario
from domain.perfil.empresa import Empresa
from domain.perfil.ruc import RUC


class EmpresaApplicationService:
    """Servicio de aplicación especializado para el ciclo de vida de perfiles de empresas (SOLID-SRP)."""

    def __init__(self, empresa_repository=None, usuario_repository=None):
        self.empresa_repository = empresa_repository
        self.usuario_repository = usuario_repository

    def update_empresa(self, usuario_id, data):
        self._require_repositories()
        self._require_empresa_user(usuario_id)
        dto = ActualizarEmpresaDTO.from_dict(data)
        empresa = self.empresa_repository.find_empresa_by_user_id(usuario_id)
        if empresa is None:
            empresa = Empresa(usuario_id=usuario_id)

        if dto.ruc is not None:
            empresa.ruc = RUC(numero=dto.ruc)

        if dto.razon_social is not None:
            empresa.razon_social = str(dto.razon_social).strip()
        if not empresa.razon_social:
            raise ValueError("La razón social es obligatoria")
        if not empresa.verificar_ruc():
            raise ValueError("El RUC no es válido")
        return self.empresa_repository.save_empresa(empresa)

    update_profile = update_empresa

    def get_empresa_profile(self, usuario_id):
        self._require_repositories()
        self._require_empresa_user(usuario_id)
        return self.empresa_repository.find_empresa_by_user_id(usuario_id)

    get_profile = get_empresa_profile

    def _require_empresa_user(self, usuario_id):
        usuario = self.usuario_repository.find_by_id(usuario_id)
        if usuario is None:
            raise ValueError("Usuario no encontrado")
        if usuario.tipo != Usuario.TIPO_EMPRESA:
            raise ValueError("El usuario no es empresa")
        if usuario.estado != Usuario.ESTADO_ACTIVO:
            raise ValueError("La cuenta no está activa")

        return usuario

    def _require_repositories(self):
        if self.empresa_repository is None:
            raise RuntimeError("EmpresaApplicationService requiere un repositorio de empresa")
        if self.usuario_repository is None:
            raise RuntimeError("EmpresaApplicationService requiere un repositorio de usuario")
