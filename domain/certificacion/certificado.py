#!/usr/bin/python
# -*- coding: utf-8 -*-

class Certificado:
    ESTADO_EMITIDO = "emitido"
    ESTADO_ANULADO = "anulado"

    def __init__(
        self,
        id=None,
        practica_id=None,
        practicante_id=None,
        codigo=None,
        estado=None,
        codigo_qr=None,
        documento=None,
        fecha_emision=None,
    ):
        self.id = id
        self.practica_id = practica_id
        self.practicante_id = practicante_id
        self.codigo = codigo
        self.estado = estado or self.ESTADO_EMITIDO
        self.codigo_qr = codigo_qr
        self.documento = documento
        self.fecha_emision = fecha_emision

    def generar_pdf(self):
        raise NotImplementedError("Generación de PDF asignada al módulo de certificación")

    def verificar_integridad(self):
        raise NotImplementedError("Verificación de integridad asignada al módulo de certificación")
