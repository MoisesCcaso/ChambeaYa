#!/usr/bin/python
# -*- coding: utf-8 -*-

from domain.convocatorias.i_convocatoria_repository import IConvocatoriaRepository

_NOT_IMPLEMENTED = "Persistencia de convocatoria asignada al módulo empresa"


class SqlAlchemyConvocatoriaRepository(IConvocatoriaRepository):
    def __init__(self):
        pass

    def save(self, convocatoria):
        raise NotImplementedError(_NOT_IMPLEMENTED)

    def find_by_id(self, convocatoria_id):
        raise NotImplementedError(_NOT_IMPLEMENTED)

    def find_abiertas(self):
        raise NotImplementedError(_NOT_IMPLEMENTED)
