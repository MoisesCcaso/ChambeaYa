#!/usr/bin/python
# -*- coding: utf-8 -*-

from datetime import datetime, timedelta, timezone
from secrets import token_urlsafe

from domain.auth.token_recuperacion import TokenRecuperacion
from werkzeug.security import check_password_hash, generate_password_hash


class AutenticacionDominioServicio:
    def generar_password_hash(self, password):
        if not password:
            raise ValueError("La contraseña es obligatoria")
        password = str(password)
        if len(password) < 8:
            raise ValueError("La contraseña debe tener al menos 8 caracteres")
        if len(password) > 128:
            raise ValueError("La contraseña no puede superar 128 caracteres")
        if not any(character.islower() for character in password):
            raise ValueError("La contraseña debe incluir una letra minúscula")
        if not any(character.isupper() for character in password):
            raise ValueError("La contraseña debe incluir una letra mayúscula")
        if not any(character.isdigit() for character in password):
            raise ValueError("La contraseña debe incluir un número")

        return generate_password_hash(password)

    def autenticar(self, usuario, password):
        if usuario is None:
            return False

        usuario.login()
        return check_password_hash(usuario.password_hash, password)

    def generar_token(self, horas_vigencia=24):
        expiracion = datetime.now(timezone.utc) + timedelta(hours=horas_vigencia)
        return TokenRecuperacion(token_urlsafe(32), expiracion)

    def validar_token(self, valor, expiracion):
        return TokenRecuperacion(valor, expiracion).esta_vigente()
