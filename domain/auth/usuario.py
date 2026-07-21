#!/usr/bin/python
# -*- coding: utf-8 -*-

import re

_EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class Usuario:
    ESTADO_ACTIVO = "activo"
    ESTADO_PENDIENTE = "pendiente"
    TIPO_EMPRESA = "empresa"
    TIPO_PRACTICANTE = "practicante"

    def __init__(
        self,
        id=None,
        email=None,
        password_hash=None,
        tipo=None,
        estado=None,
        activation_token=None,
        activation_token_expires_at=None,
        password_reset_token=None,
        password_reset_expires_at=None,
    ):
        self.id = id
        self.email = email
        self.password_hash = password_hash
        self.tipo = tipo
        self.estado = estado or self.ESTADO_PENDIENTE
        self.activation_token = activation_token
        self.activation_token_expires_at = activation_token_expires_at
        self.password_reset_token = password_reset_token
        self.password_reset_expires_at = password_reset_expires_at

    def registrar(self):
        if not self.email:
            raise ValueError("El email es obligatorio")
        if not _EMAIL_REGEX.match(self.email):
            raise ValueError("El email no tiene un formato válido")
        if not self.password_hash:
            raise ValueError("La contraseña es obligatoria")
        if self.tipo not in {self.TIPO_PRACTICANTE, self.TIPO_EMPRESA}:
            raise ValueError("El tipo de usuario no es válido")

        return self

    def login(self):
        if self.estado != self.ESTADO_ACTIVO:
            raise ValueError("La cuenta no está activa")

        return self

    def activar(self):
        self.estado = self.ESTADO_ACTIVO
        self.activation_token = None
        self.activation_token_expires_at = None
        return self

    def asignar_token_activacion(self, token):
        self.activation_token = token.valor
        self.activation_token_expires_at = token.expiracion
        return self

    def asignar_token_recuperacion(self, token):
        self.password_reset_token = token.valor
        self.password_reset_expires_at = token.expiracion
        return self

    def actualizar_password(self, password_hash):
        if not password_hash:
            raise ValueError("La contraseña es obligatoria")

        self.password_hash = password_hash
        self.password_reset_token = None
        self.password_reset_expires_at = None
        return self
