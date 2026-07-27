# domain/convocatorias/i_postulacion_repository.py
from abc import ABC, abstractmethod
from typing import List, Optional
from .postulacion import Postulacion

class IPostulacionRepository(ABC):
    """Interfaz para el repositorio de postulaciones."""

    @abstractmethod
    def guardar(self, postulacion: Postulacion) -> Postulacion:
        """Guarda una postulación."""
        pass

    @abstractmethod
    def obtener_por_id(self, postulacion_id: int) -> Optional[Postulacion]:
        """Obtiene una postulación por su ID."""
        pass

    @abstractmethod
    def obtener_por_practicante(self, practicante_id: int) -> List[Postulacion]:
        """Obtiene todas las postulaciones de un practicante."""
        pass

    @abstractmethod
    def obtener_por_convocatoria(self, convocatoria_id: int) -> List[Postulacion]:
        """Obtiene todas las postulaciones de una convocatoria."""
        pass

    @abstractmethod
    def obtener_por_practicante_y_convocatoria(self, practicante_id: int, convocatoria_id: int) -> Optional[Postulacion]:
        """Obtiene una postulación específica."""
        pass

    @abstractmethod
    def actualizar_estado(self, postulacion_id: int, nuevo_estado: str) -> Postulacion:
        """Actualiza el estado de una postulación."""
        pass

    @abstractmethod
    def eliminar(self, postulacion_id: int) -> bool:
        """Elimina una postulación."""
        pass