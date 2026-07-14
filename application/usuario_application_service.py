#!/usr/bin/python
# -*- coding: utf-8 -*-

from domain.auth.autenticacion_dominio_servicio import AutenticacionDominioServicio
from domain.auth.usuario import Usuario


class UsuarioApplicationService:
    def __init__(self, usuario_repository=None, autenticacion_dominio_servicio=None):
        self.usuario_repository = usuario_repository
        self.autenticacion_dominio_servicio = (
            autenticacion_dominio_servicio or AutenticacionDominioServicio()
        )

    def register_user(self, email, password, tipo):
        self._require_repository()

        normalized_email = self._normalize_email(email)
        if self.usuario_repository.find_by_email(normalized_email) is not None:
            raise ValueError("El email ya está registrado")

        password_hash = self.autenticacion_dominio_servicio.generar_password_hash(password)
        usuario = Usuario(
            email=normalized_email,
            password_hash=password_hash,
            tipo=tipo,
            estado=Usuario.ESTADO_ACTIVO,
        )
        usuario.registrar()

        return self.usuario_repository.save(usuario)

    def authenticate(self, email, password):
        self._require_repository()

        usuario = self.usuario_repository.find_by_email(self._normalize_email(email))
        if not self.autenticacion_dominio_servicio.autenticar(usuario, password):
            raise ValueError("Credenciales inválidas")

        return usuario

    def recover_password(self):
        pass

    def activate_account(self):
        pass

    def find_by_id(self, usuario_id):
        self._require_repository()
        return self.usuario_repository.find_by_id(usuario_id)

    def _require_repository(self):
        if self.usuario_repository is None:
            raise RuntimeError("UsuarioApplicationService requiere un repositorio")

    def _normalize_email(self, email):
        if not email:
            raise ValueError("El email es obligatorio")

        return email.strip().lower()
