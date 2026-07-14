#!/usr/bin/python
# -*- coding: utf-8 -*-

from werkzeug.security import check_password_hash, generate_password_hash


class AutenticacionDominioServicio:
    def __init__(self):
        pass

    def generar_password_hash(self, password):
        if not password:
            raise ValueError("La contraseña es obligatoria")

        return generate_password_hash(password)

    def autenticar(self, usuario, password):
        if usuario is None:
            return False

        usuario.login()
        return check_password_hash(usuario.password_hash, password)

    def validar_token(self):
        pass
