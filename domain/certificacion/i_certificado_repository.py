#!/usr/bin/python
# -*- coding: utf-8 -*-

from abc import ABC, abstractmethod


class ICertificadoRepository(ABC):
    @abstractmethod
    def save(self):
        pass

    @abstractmethod
    def find_by_id(self):
        pass

    @abstractmethod
    def find_by_codigo(self):
        pass
