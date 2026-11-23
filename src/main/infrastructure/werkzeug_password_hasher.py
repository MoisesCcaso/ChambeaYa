#!/usr/bin/python
# -*- coding: utf-8 -*-

from werkzeug.security import check_password_hash, generate_password_hash

from domain.auth.i_password_hasher import IPasswordHasher


class WerkzeugPasswordHasher(IPasswordHasher):
    def hash(self, password):
        return generate_password_hash(password)

    def verify(self, password_hash, password):
        return check_password_hash(password_hash, password)