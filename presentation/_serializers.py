#!/usr/bin/python
# -*- coding: utf-8 -*-

def format_fecha(fecha):
    if fecha is None:
        return None

    return fecha.isoformat()
