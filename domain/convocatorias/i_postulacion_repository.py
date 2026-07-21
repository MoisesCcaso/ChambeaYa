#!/usr/bin/python
# -*- coding: utf-8 -*-

from abc import ABC, abstractmethod


class IPostulacionRepository(ABC):
    @abstractmethod
    def save(self, postulacion):
        pass

    @abstractmethod
    def find_by_id(self, postulacion_id):
        pass

    @abstractmethod
    def find_by_practicante_and_convocatoria(self, practicante_id, convocatoria_id):
        pass
