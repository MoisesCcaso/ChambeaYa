#!/usr/bin/python
# -*- coding: utf-8 -*-

from abc import ABC, abstractmethod


class IPasswordHasher(ABC):
    """Puerto del dominio para hashear y verificar contraseñas."""

    @abstractmethod
    def hash(self, password):
        pass

    @abstractmethod
    def verify(self, password_hash, password):
        pass