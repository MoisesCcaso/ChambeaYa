#!/usr/bin/python
# -*- coding: utf-8 -*-

class Usuario:
    ESTADO_ACTIVO = "activo"
    ESTADO_PENDIENTE = "pendiente"
    TIPO_EMPRESA = "empresa"
    TIPO_PRACTICANTE = "practicante"

    def __init__(self, id=None, email=None, password_hash=None, tipo=None, estado=None):
        self.id = id
        self.email = email
        self.password_hash = password_hash
        self.tipo = tipo
        self.estado = estado or self.ESTADO_PENDIENTE

    def registrar(self):
        if not self.email:
            raise ValueError("El email es obligatorio")
        if not self.password_hash:
            raise ValueError("La contraseña es obligatoria")
        if self.tipo not in {self.TIPO_PRACTICANTE, self.TIPO_EMPRESA}:
            raise ValueError("El tipo de usuario no es válido")

        return self

    def login(self):
        if self.estado != self.ESTADO_ACTIVO:
            raise ValueError("La cuenta no está activa")

        return self
