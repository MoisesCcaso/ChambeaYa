#!/usr/bin/python
# -*- coding: utf-8 -*-
from abc import ABC, abstractmethod


class INotificacionReader(ABC):
    @abstractmethod
    def find_by_usuario_id(self, usuario_id):
        pass

    @abstractmethod
    def find_unread_by_usuario_id(self, usuario_id):
        pass

    @abstractmethod
    def count_unread(self, usuario_id):
        pass
