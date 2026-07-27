# domain/matching/i_sugerencia_repository.py
from abc import ABC, abstractmethod
from typing import List, Optional
from .sugerencia import Sugerencia

class ISugerenciaRepository(ABC):
    """Interfaz para el repositorio de sugerencias."""

    @abstractmethod
    def guardar(self, sugerencia: Sugerencia) -> Sugerencia:
        """Guarda una sugerencia."""
        pass

    @abstractmethod
    def guardar_multiples(self, sugerencias: List[Sugerencia]) -> List[Sugerencia]:
        """Guarda múltiples sugerencias."""
        pass

    @abstractmethod
    def obtener_por_practicante(self, practicante_id: int) -> List[Sugerencia]:
        """Obtiene todas las sugerencias de un practicante."""
        pass

    @abstractmethod
    def obtener_por_convocatoria(self, convocatoria_id: int) -> List[Sugerencia]:
        """Obtiene todas las sugerencias de una convocatoria."""
        pass

    @abstractmethod
    def eliminar_por_practicante(self, practicante_id: int) -> int:
        """Elimina todas las sugerencias de un practicante."""
        pass

    @abstractmethod
    def limpiar_antiguas(self, dias: int) -> int:
        """Elimina sugerencias más antiguas que X días."""
        pass