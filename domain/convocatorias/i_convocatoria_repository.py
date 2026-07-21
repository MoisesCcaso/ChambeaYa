#!/usr/bin/python
# -*- coding: utf-8 -*-

from abc import ABC, abstractmethod


class IConvocatoriaRepository(ABC):
    @abstractmethod
    def save(self, convocatoria):
        pass

    @abstractmethod
    def find_by_id(self, convocatoria_id):
        pass

    @abstractmethod
    def find_abiertas(self):
        pass
