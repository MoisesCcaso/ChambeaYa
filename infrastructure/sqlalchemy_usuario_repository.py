#!/usr/bin/python
# -*- coding: utf-8 -*-

from domain.auth.i_usuario_repository import IUsuarioRepository


class SqlAlchemyUsuarioRepository(IUsuarioRepository):
    def __init__(self):
        pass

    def save(self):
        pass

    def find_by_email(self):
        pass

    def find_by_id(self):
        pass
