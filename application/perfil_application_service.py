#!/usr/bin/python
# -*- coding: utf-8 -*-

from domain.auth.usuario import Usuario
from domain.perfil.practicante import Practicante


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
            dni=data.get("dni"),
            carnet_universitario=data.get("carnet_universitario"),
        )

        for habilidad in data.get("habilidades", []) or []:
            practicante.agregar_habilidad(habilidad)

        for formacion in data.get("formacion_educativa", []) or []:
            practicante.agregar_formacion(formacion)

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

    def update_empresa(self):
        raise NotImplementedError("El perfil de empresa no pertenece a RF.2")

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

    def _require_repositories(self):
        if self.perfil_repository is None:
            raise RuntimeError("PerfilApplicationService requiere un repositorio de perfil")
        if self.usuario_repository is None:
            raise RuntimeError("PerfilApplicationService requiere un repositorio de usuario")
