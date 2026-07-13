#!/usr/bin/python
# -*- coding: utf-8 -*-

from domain.practica_evaluacion.i_practica_repository import IPracticaRepository


class SqlAlchemyPracticaRepository(IPracticaRepository):
    def __init__(self):
        pass

    def save(self):
        pass

    def find_by_id(self):
        pass

    def find_by_practicante_id(self):
        pass
