#!/usr/bin/python
# -*- coding: utf-8 -*-

from abc import ABC, abstractmethod


class IPracticaRepository(ABC):
    @abstractmethod
    def save(self, practica):
        pass

    @abstractmethod
    def find_by_id(self, practica_id):
        pass

    @abstractmethod
    def find_by_practicante_id(self, practicante_id):
        pass
