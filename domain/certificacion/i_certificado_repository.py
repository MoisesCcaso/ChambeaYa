#!/usr/bin/python
# -*- coding: utf-8 -*-

from abc import ABC, abstractmethod


class ICertificadoRepository(ABC):
    @abstractmethod
    def save(self, certificado):
        pass

    @abstractmethod
    def find_by_id(self, certificado_id):
        pass

    @abstractmethod
    def find_by_codigo(self, codigo):
        pass

    @abstractmethod
    def find_by_practicante_id(self, practicante_id):
        pass
