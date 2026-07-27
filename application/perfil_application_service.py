#!/usr/bin/python
# -*- coding: utf-8 -*-

from domain.auth.usuario import Usuario
from domain.perfil.practicante import Practicante
from domain.perfil.empresa import Empresa
from domain.perfil.ruc import RUC

class PerfilApplicationService:
    def __init__(self, perfil_repository=None, usuario_repository=None):
        self.perfil_repository = perfil_repository
        self.usuario_repository = usuario_repository

    def get_practicante_profile(self, usuario_id):
        self._require_repositories()
        self._require_practicante_user(usuario_id)
        return self.perfil_repository.find_practicante_by_user_id(usuario_id)

    def update_practicante(self, usuario_id, data):
        self._require_repositories()
        self._require_practicante_user(usuario_id)

        practicante = self.perfil_repository.find_practicante_by_user_id(usuario_id)
        if practicante is None:
            practicante = Practicante(usuario_id=usuario_id)

        practicante.actualizar_datos(
            nombres=data.get("nombres"),
            apellidos=data.get("apellidos"),
        )

        identidad_actualizada = "dni" in data or "carnet_universitario" in data
        if "dni" in data:
            practicante.dni = self._optional_text(data.get("dni"))
        if "carnet_universitario" in data:
            practicante.carnet_universitario = self._optional_text(
                data.get("carnet_universitario")
            )
        if "habilidades" in data:
            practicante.reemplazar_habilidades(data.get("habilidades") or [])
        if "formacion_educativa" in data:
            practicante.reemplazar_formacion(data.get("formacion_educativa") or [])

        if identidad_actualizada:
            if practicante.dni or practicante.carnet_universitario:
                practicante.verificar_identidad()
            else:
                practicante.identidad_verificada = False

        practicante.calcular_score()
        return self.perfil_repository.save_practicante(practicante)

    def add_habilidad(self, usuario_id, habilidad):
        self._require_repositories()
        practicante = self._get_or_create_practicante(usuario_id)
        practicante.agregar_habilidad(habilidad)
        practicante.calcular_score()
        return self.perfil_repository.save_practicante(practicante)

    def add_formacion(self, usuario_id, formacion):
        self._require_repositories()
        practicante = self._get_or_create_practicante(usuario_id)
        practicante.agregar_formacion(formacion)
        practicante.calcular_score()
        return self.perfil_repository.save_practicante(practicante)

    def register_identity(self, usuario_id, dni=None, carnet_universitario=None):
        self._require_repositories()
        practicante = self._get_or_create_practicante(usuario_id)
        practicante.actualizar_datos(dni=dni, carnet_universitario=carnet_universitario)
        practicante.verificar_identidad()
        practicante.calcular_score()
        return self.perfil_repository.save_practicante(practicante)

    def update_empresa(self, usuario_id, data):
        self._require_repositories()
        self._require_empresa_user(usuario_id)
        empresa = self.perfil_repository.find_empresa_by_user_id(usuario_id)
        if empresa is None:
            empresa = Empresa(usuario_id=usuario_id)

        numero_ruc = data.get("ruc")
        if numero_ruc is not None:
            empresa.ruc = RUC(numero=numero_ruc)

        if data.get("razon_social") is not None:
            empresa.razon_social = str(data["razon_social"]).strip()
        if not empresa.razon_social:
            raise ValueError("La razón social es obligatoria")
        if not empresa.verificar_ruc():
            raise ValueError("El RUC no es válido")
        return self.perfil_repository.save_empresa(empresa)

    def get_empresa_profile(self, usuario_id):
        self._require_repositories()
        self._require_empresa_user(usuario_id)
        return self.perfil_repository.find_empresa_by_user_id(usuario_id)

    def verify_profile(self, usuario_id):
        self._require_repositories()
        practicante = self.perfil_repository.find_practicante_by_user_id(usuario_id)
        if practicante is None:
            raise ValueError("Perfil de practicante no encontrado")

        return practicante.identidad_verificada

    def get_reputation_score(self, usuario_id):
        self._require_repositories()
        practicante = self.perfil_repository.find_practicante_by_user_id(usuario_id)
        if practicante is None:
            return 0.0

        return practicante.score_reputacion

    def _get_or_create_practicante(self, usuario_id):
        self._require_practicante_user(usuario_id)
        practicante = self.perfil_repository.find_practicante_by_user_id(usuario_id)
        if practicante is None:
            practicante = Practicante(usuario_id=usuario_id)

        return practicante

    def _require_practicante_user(self, usuario_id):
        usuario = self.usuario_repository.find_by_id(usuario_id)
        if usuario is None:
            raise ValueError("Usuario no encontrado")
        if usuario.tipo != Usuario.TIPO_PRACTICANTE:
            raise ValueError("El usuario no es practicante")
        if usuario.estado != Usuario.ESTADO_ACTIVO:
            raise ValueError("La cuenta no está activa")

        return usuario
    
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
        if self.perfil_repository is None:
            raise RuntimeError("PerfilApplicationService requiere un repositorio de perfil")
        if self.usuario_repository is None:
            raise RuntimeError("PerfilApplicationService requiere un repositorio de usuario")

    def _optional_text(self, value):
        if value is None:
            return None
        normalized = str(value).strip()
        return normalized or None
