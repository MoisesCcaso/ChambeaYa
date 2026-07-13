#!/usr/bin/python
# -*- coding: utf-8 -*-

from domain.certificacion.i_certificado_repository import ICertificadoRepository


class SqlAlchemyCertificadoRepository(ICertificadoRepository):
    def __init__(self):
        pass

    def save(self):
        pass

    def find_by_id(self):
        pass

    def find_by_codigo(self):
        pass
