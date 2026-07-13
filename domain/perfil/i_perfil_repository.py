#!/usr/bin/python
# -*- coding: utf-8 -*-

from abc import ABC, abstractmethod


class IPerfilRepository(ABC):
    @abstractmethod
    def save_practicante(self):
        pass

    @abstractmethod
    def save_empresa(self):
        pass

    @abstractmethod
    def find_by_user_id(self):
        pass
