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
            estado=Usuario.ESTADO_PENDIENTE,
        )
        usuario.registrar()
        usuario.asignar_token_activacion(
            self.autenticacion_dominio_servicio.generar_token(horas_vigencia=48)
        )

        return self.usuario_repository.save(usuario)

    def authenticate(self, email, password):
        self._require_repository()

        usuario = self.usuario_repository.find_by_email(self._normalize_email(email))
        if not self.autenticacion_dominio_servicio.autenticar(usuario, password):
            raise ValueError("Credenciales inválidas")

        return usuario

    def recover_password(self, email):
        self._require_repository()

        usuario = self.usuario_repository.find_by_email(self._normalize_email(email))
        if usuario is None:
            return None

        usuario.asignar_token_recuperacion(
            self.autenticacion_dominio_servicio.generar_token(horas_vigencia=2)
        )
        return self.usuario_repository.save(usuario)

    def activate_account(self, token):
        self._require_repository()

        if not token:
            raise ValueError("El token de activación es obligatorio")

        usuario = self.usuario_repository.find_by_activation_token(token)
        if usuario is None:
            raise ValueError("Token de activación inválido")

        if not self.autenticacion_dominio_servicio.validar_token(
            usuario.activation_token,
            usuario.activation_token_expires_at,
        ):
            raise ValueError("Token de activación expirado")

        usuario.activar()
        return self.usuario_repository.save(usuario)

    def reset_password(self, token, new_password):
        self._require_repository()

        if not token:
            raise ValueError("El token de recuperación es obligatorio")

        usuario = self.usuario_repository.find_by_password_reset_token(token)
        if usuario is None:
            raise ValueError("Token de recuperación inválido")

        if not self.autenticacion_dominio_servicio.validar_token(
            usuario.password_reset_token,
            usuario.password_reset_expires_at,
        ):
            raise ValueError("Token de recuperación expirado")

        password_hash = self.autenticacion_dominio_servicio.generar_password_hash(new_password)
        usuario.actualizar_password(password_hash)
        return self.usuario_repository.save(usuario)

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
