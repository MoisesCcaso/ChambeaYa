#!/usr/bin/python
# -*- coding: utf-8 -*-

from domain.convocatorias.i_postulacion_repository import IPostulacionRepository

_NOT_IMPLEMENTED = "Persistencia de postulación pendiente (modelo ORM no disponible)"


class SqlAlchemyPostulacionRepository(IPostulacionRepository):
    def __init__(self):
        pass

    def save(self, postulacion):
        raise NotImplementedError(_NOT_IMPLEMENTED)

    def find_by_id(self, postulacion_id):
        raise NotImplementedError(_NOT_IMPLEMENTED)

    def find_by_practicante_and_convocatoria(self, practicante_id, convocatoria_id):
        raise NotImplementedError(_NOT_IMPLEMENTED)
