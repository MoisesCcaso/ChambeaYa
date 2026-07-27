# domain/convocatorias/i_convocatoria_repository.py
# LAB 12 - SOLID: I (Segregación de Interfaces)
# La interfaz grande se divide en interfaces más pequeñas y específicas.

from abc import ABC, abstractmethod
from typing import List, Optional
from domain.convocatorias.convocatoria import Convocatoria


class IConvocatoriaRepositoryLectura(ABC):
    """Interfaz específica para operaciones de lectura."""
    
    @abstractmethod
    def obtener_por_id(self, convocatoria_id: int) -> Optional[Convocatoria]:
        pass

    @abstractmethod
    def listar_activas(self) -> List[Convocatoria]:
        pass

    @abstractmethod
    def listar_por_empresa(self, empresa_id: int) -> List[Convocatoria]:
        pass


class IConvocatoriaRepositoryEscritura(ABC):
    """Interfaz específica para operaciones de escritura."""
    
    @abstractmethod
    def guardar(self, convocatoria: Convocatoria) -> Convocatoria:
        pass

    @abstractmethod
    def actualizar(self, convocatoria: Convocatoria) -> Convocatoria:
        pass

    @abstractmethod
    def eliminar(self, convocatoria_id: int) -> bool:
        pass


# La interfaz principal extiende las dos interfaces específicas
class IConvocatoriaRepository(IConvocatoriaRepositoryLectura, IConvocatoriaRepositoryEscritura):
    """
    Interfaz completa que hereda de las interfaces segregadas.
    Las clases que implementen esta interfaz deben cumplir con todos los métodos.
    """
    pass