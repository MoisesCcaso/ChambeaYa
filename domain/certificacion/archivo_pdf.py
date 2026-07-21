#!/usr/bin/python
# -*- coding: utf-8 -*-

class ArchivoPDF:
    def __init__(self, url=None, hash_integridad=None):
        self.url = url
        self.hash_integridad = hash_integridad

    def verificar_integridad(self):
        raise NotImplementedError("Verificación de integridad asignada al módulo de certificación")
