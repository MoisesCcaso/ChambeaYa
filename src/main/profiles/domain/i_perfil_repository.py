from abc import ABC
from profiles.domain.i_practicante_repository import IPracticanteRepository
from profiles.domain.i_empresa_repository import IEmpresaRepository


class IPerfilRepository(IPracticanteRepository, IEmpresaRepository, ABC):
    """Interfaz consolidada de perfil mantenida para compatibilidad de contratos agregados (SOLID-ISP)."""
    pass

