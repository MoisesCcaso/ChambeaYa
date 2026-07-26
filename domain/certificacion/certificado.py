#!/usr/bin/python
# -*- coding: utf-8 -*-
from domain.certificacion.archivo_pdf import ArchivoPDF

class Certificado:
    def __init__(self, id=None, practica_id=None, codigo_qr=None, documento=None):
        self.id = id
        self.practica_id = practica_id
        self.codigo_qr = codigo_qr
        self.documento = documento

    def generar_pdf(self, contenido):
        self.documento = ArchivoPDF.crear(self.practica_id, contenido)
        return self.documento

    def verificar_integridad(self, contenido):
        if self.documento is None:
            return False
        return self.documento.verificar_integridad(contenido)