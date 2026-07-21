#!/usr/bin/python
# -*- coding: utf-8 -*-

class CodigoQR:
    def __init__(self, valor=None, url_verificacion=None, hash_integridad=None):
        self.valor = valor
        self.url_verificacion = url_verificacion
        self.hash_integridad = hash_integridad

    def generar(self):
        raise NotImplementedError("Generación de código QR asignada al módulo de certificación")

    def verificar(self):
        raise NotImplementedError("Verificación de código QR asignada al módulo de certificación")
