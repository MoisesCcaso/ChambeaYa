#!/usr/bin/python
# -*- coding: utf-8 -*-
import hashlib
from uuid import uuid4
class CodigoQR:
    def __init__(self, valor=None, url_verificacion=None, hash_integridad=None):
         self.valor = valor
         self.url_verificacion = url_verificacion
         self.hash_integridad = hash_integridad

    @staticmethod
    def generar(practica_id):
        valor = f"CERT-{practica_id}-{uuid4().hex[:8]}"
        url_verificacion = f"/certificados/verificar/{valor}"
        hash_integridad = hashlib.sha256(valor.encode()).hexdigest()
        return CodigoQR(valor=valor, url_verificacion=url_verificacion, hash_integridad=hash_integridad)

    def verificar(self, valor_a_verificar):
        return self.valor == valor_a_verificar
