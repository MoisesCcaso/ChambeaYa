#!/usr/bin/python
# -*- coding: utf-8 -*-
from abc import ABC, abstractmethod


class INotificacionWriter(ABC):
    @abstractmethod
    def save(self, notificacion):
        pass

    @abstractmethod
    def mark_as_read(self, usuario_id, notificacion_id):
        pass

    @abstractmethod
    def mark_all_as_read(self, usuario_id):
        pass
