#!/usr/bin/python
# -*- coding: utf-8 -*-

from abc import ABC, abstractmethod


class IUsuarioRepository(ABC):
    @abstractmethod
    def save(self, usuario):
        pass

    @abstractmethod
    def find_by_email(self, email):
        pass

    @abstractmethod
    def find_by_id(self, usuario_id):
        pass

    @abstractmethod
    def find_by_activation_token(self, token):
        pass

    @abstractmethod
    def find_by_password_reset_token(self, token):
        pass
