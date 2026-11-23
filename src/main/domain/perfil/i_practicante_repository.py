#!/usr/bin/python
# -*- coding: utf-8 -*-

from abc import ABC, abstractmethod


class IPracticanteRepository(ABC):
    @abstractmethod
    def save_practicante(self, practicante):
        pass

    @abstractmethod
    def find_practicante_by_user_id(self, usuario_id):
        pass

    @abstractmethod
    def find_practicante_by_id(self, practicante_id):
        pass
