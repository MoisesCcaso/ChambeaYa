#!/usr/bin/python
# -*- coding: utf-8 -*-

from application.dtos import ActualizarPracticanteDTO, UNSET
from domain.auth.usuario import Usuario
from domain.perfil.practicante import Practicante


class PracticanteApplicationService:
    """Servicio de aplicación especializado para el ciclo de vida de perfiles de practicantes (SOLID-SRP)."""

    def __init__(self, practicante_repository=None, usuario_repository=None):
        self.practicante_repository = practicante_repository
        self.usuario_repository = usuario_repository

    def get_practicante_profile(self, usuario_id):
        self._require_repositories()
        self._require_practicante_user(usuario_id)
        return self.practicante_repository.find_practicante_by_user_id(usuario_id)

    get_profile = get_practicante_profile

    def update_practicante(self, usuario_id, data):
        self._require_repositories()
        self._require_practicante_user(usuario_id)
        dto = ActualizarPracticanteDTO.from_dict(data)

        practicante = self.practicante_repository.find_practicante_by_user_id(usuario_id)
        if practicante is None:
            practicante = Practicante(usuario_id=usuario_id)

        practicante.actualizar_datos(
            nombres=dto.nombres,
            apellidos=dto.apellidos,
        )

        identidad_actualizada = (
            dto.dni is not UNSET or dto.carnet_universitario is not UNSET
        )
        if dto.dni is not UNSET:
            practicante.dni = self._optional_text(dto.dni)
        if dto.carnet_universitario is not UNSET:
            practicante.carnet_universitario = self._optional_text(
                dto.carnet_universitario
            )
        if dto.habilidades is not UNSET:
            practicante.reemplazar_habilidades(dto.habilidades or [])
        if dto.formacion_educativa is not UNSET:
            practicante.reemplazar_formacion(dto.formacion_educativa or [])

        if identidad_actualizada:
            if practicante.dni or practicante.carnet_universitario:
                practicante.verificar_identidad()
            else:
                practicante.identidad_verificada = False

        practicante.calcular_score()
        return self.practicante_repository.save_practicante(practicante)

    update_profile = update_practicante

    def add_habilidad(self, usuario_id, habilidad):
        self._require_repositories()
        practicante = self._get_or_create_practicante(usuario_id)
        practicante.agregar_habilidad(habilidad)
        practicante.calcular_score()
        return self.practicante_repository.save_practicante(practicante)

    def add_formacion(self, usuario_id, formacion):
        self._require_repositories()
        practicante = self._get_or_create_practicante(usuario_id)
        practicante.agregar_formacion(formacion)
        practicante.calcular_score()
        return self.practicante_repository.save_practicante(practicante)

    def register_identity(self, usuario_id, dni=None, carnet_universitario=None):
        self._require_repositories()
        practicante = self._get_or_create_practicante(usuario_id)
        practicante.actualizar_datos(dni=dni, carnet_universitario=carnet_universitario)
        practicante.verificar_identidad()
        practicante.calcular_score()
        return self.practicante_repository.save_practicante(practicante)

    def verify_profile(self, usuario_id):
        self._require_repositories()
        practicante = self.practicante_repository.find_practicante_by_user_id(usuario_id)
        if practicante is None:
            raise ValueError("Perfil de practicante no encontrado")

        return practicante.identidad_verificada

    def get_reputation_score(self, usuario_id):
        self._require_repositories()
        practicante = self.practicante_repository.find_practicante_by_user_id(usuario_id)
        if practicante is None:
            return 0.0

        return practicante.score_reputacion

    def _get_or_create_practicante(self, usuario_id):
        self._require_practicante_user(usuario_id)
        practicante = self.practicante_repository.find_practicante_by_user_id(usuario_id)
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
        if self.practicante_repository is None:
            raise RuntimeError("PracticanteApplicationService requiere un repositorio de practicante")
        if self.usuario_repository is None:
            raise RuntimeError("PracticanteApplicationService requiere un repositorio de usuario")

    def _optional_text(self, value):
        if value is None:
            return None
        normalized = str(value).strip()
        return normalized or None
