#!/usr/bin/python
# -*- coding: utf-8 -*-

from abc import ABC, abstractmethod


class IPerfilRepository(ABC):
    @abstractmethod
    def save_practicante(self, practicante):
        pass

    @abstractmethod
    def save_empresa(self, empresa):
        pass

    @abstractmethod
    def find_practicante_by_user_id(self, usuario_id):
        pass
    @abstractmethod

    def find_practicante_by_id(self, practicante_id):
        pass

    @abstractmethod
    def find_empresa_by_user_id(self, usuario_id):
        pass
