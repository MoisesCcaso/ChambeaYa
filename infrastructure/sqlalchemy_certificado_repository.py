#!/usr/bin/python
# -*- coding: utf-8 -*-

from domain.certificacion.i_certificado_repository import ICertificadoRepository

_NOT_IMPLEMENTED = "Persistencia de certificado pendiente (modelo ORM no disponible)"


class SqlAlchemyCertificadoRepository(ICertificadoRepository):
    def __init__(self):
        pass

    def save(self, certificado):
        raise NotImplementedError(_NOT_IMPLEMENTED)

    def find_by_id(self, certificado_id):
        raise NotImplementedError(_NOT_IMPLEMENTED)

    def find_by_codigo(self, codigo):
        raise NotImplementedError(_NOT_IMPLEMENTED)

    def find_by_practicante_id(self, practicante_id):
        raise NotImplementedError(_NOT_IMPLEMENTED)
