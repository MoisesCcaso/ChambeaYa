#!/usr/bin/python
# -*- coding: utf-8 -*-

from abc import ABC
from domain.perfil.i_practicante_repository import IPracticanteRepository
from domain.perfil.i_empresa_repository import IEmpresaRepository


class IPerfilRepository(IPracticanteRepository, IEmpresaRepository, ABC):
    """Interfaz consolidada de perfil mantenida para compatibilidad de contratos agregados (SOLID-ISP)."""
    pass

