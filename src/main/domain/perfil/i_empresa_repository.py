#!/usr/bin/python
# -*- coding: utf-8 -*-

from abc import ABC, abstractmethod


class IEmpresaRepository(ABC):
    @abstractmethod
    def save_empresa(self, empresa):
        pass

    @abstractmethod
    def find_empresa_by_user_id(self, usuario_id):
        pass
