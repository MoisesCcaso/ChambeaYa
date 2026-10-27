#!/usr/bin/python
# -*- coding: utf-8 -*-
import hashlib
class ArchivoPDF:
    def __init__(self, url=None, hash_integridad=None, contenido=None):
        self.url = url
        self.hash_integridad = hash_integridad
        self.contenido = contenido

    @staticmethod
    def crear(practica_id, contenido):
        if not contenido:
            raise ValueError("Debe proveerse el contenido del PDF para generar el archivo")

        contenido_bytes = contenido.encode() if isinstance(contenido, str) else contenido
        url = f"/certificados/practica/{practica_id}/pdf"
        hash_integridad = hashlib.sha256(contenido_bytes).hexdigest()
        return ArchivoPDF(
            url=url,
            hash_integridad=hash_integridad,
            contenido=contenido_bytes.decode("utf-8"),
        )

    def verificar_integridad(self, contenido):
        if contenido is None or not self.hash_integridad:
            return False
        contenido_bytes = contenido.encode() if isinstance(contenido, str) else contenido
        return hashlib.sha256(contenido_bytes).hexdigest() == self.hash_integridad
