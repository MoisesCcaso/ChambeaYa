#!/usr/bin/python
# -*- coding: utf-8 -*-

from abc import ABC, abstractmethod


class ISugerenciaRepository(ABC):
    @abstractmethod
    def save(self, sugerencia):
        pass

    @abstractmethod
    def find_by_practicante_id(self, practicante_id):
        pass
