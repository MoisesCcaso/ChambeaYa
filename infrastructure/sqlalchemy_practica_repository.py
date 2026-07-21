#!/usr/bin/python
# -*- coding: utf-8 -*-

from domain.practica_evaluacion.i_practica_repository import IPracticaRepository

_NOT_IMPLEMENTED = "Persistencia de práctica pendiente (modelo ORM no disponible)"


class SqlAlchemyPracticaRepository(IPracticaRepository):
    def __init__(self):
        pass

    def save(self, practica):
        raise NotImplementedError(_NOT_IMPLEMENTED)

    def find_by_id(self, practica_id):
        raise NotImplementedError(_NOT_IMPLEMENTED)

    def find_by_practicante_id(self, practicante_id):
        raise NotImplementedError(_NOT_IMPLEMENTED)
