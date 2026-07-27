#!/usr/bin/python
# -*- coding: utf-8 -*-

class NombreCompleto:
    def __init__(self, nombres=None, apellidos=None):
        self.nombres = nombres
        self.apellidos = apellidos

    def validar(self):
        nombres = str(self.nombres or "").strip()
        apellidos = str(self.apellidos or "").strip()
        if not nombres or not apellidos:
            raise ValueError("Nombres y apellidos son obligatorios")
        self.nombres = nombres
        self.apellidos = apellidos
        return self

    def __str__(self):
        return f"{self.nombres} {self.apellidos}".strip()
