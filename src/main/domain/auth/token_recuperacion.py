#!/usr/bin/python
# -*- coding: utf-8 -*-

from datetime import datetime, timezone


class TokenRecuperacion:
    def __init__(self, valor=None, expiracion=None):
        self.valor = valor
        self.expiracion = expiracion

    def esta_vigente(self):
        if not self.valor or self.expiracion is None:
            return False

        expiracion = self.expiracion
        if expiracion.tzinfo is None:
            expiracion = expiracion.replace(tzinfo=timezone.utc)

        return expiracion > datetime.now(timezone.utc)
