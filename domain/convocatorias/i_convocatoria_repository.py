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
    def find_all(self):
        pass

    @abstractmethod
    def search(self, query=None, estado=None):
        pass

    @abstractmethod
    def find_by_empresa_id(self, empresa_id):
        pass
