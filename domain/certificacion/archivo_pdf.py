#!/usr/bin/python
# -*- coding: utf-8 -*-
import hashlib
class ArchivoPDF:
    def __init__(self, url=None, hash_integridad=None):
        self.url = url
        self.hash_integridad = hash_integridad

    @staticmethod
    def crear(practica_id, contenido):
        if not contenido:
            raise ValueError("Debe proveerse el contenido del PDF para generar el archivo")

        contenido_bytes = contenido.encode() if isinstance(contenido, str) else contenido
        url = f"/certificados/pdf/practica-{practica_id}.pdf"
        hash_integridad = hashlib.sha256(contenido_bytes).hexdigest()
        return ArchivoPDF(url=url, hash_integridad=hash_integridad)

    def verificar_integridad(self, contenido):
        contenido_bytes = contenido.encode() if isinstance(contenido, str) else contenido
        return hashlib.sha256(contenido_bytes).hexdigest() == self.hash_integridad
