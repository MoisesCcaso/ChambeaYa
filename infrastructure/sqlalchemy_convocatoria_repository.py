#!/usr/bin/python
# -*- coding: utf-8 -*-

from domain.convocatorias.i_convocatoria_repository import IConvocatoriaRepository


class SqlAlchemyConvocatoriaRepository(IConvocatoriaRepository):
    def __init__(self):
        pass

    def save(self):
        pass

    def find_by_id(self):
        pass

    def search(self):
        pass
