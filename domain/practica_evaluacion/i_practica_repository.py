# domain/practica_evaluacion/i_practica_repository.py
from abc import ABC, abstractmethod
from typing import List, Optional
from .practica import Practica

class IPracticaRepository(ABC):
    """Interfaz para el repositorio de prácticas."""

    @abstractmethod
    def guardar(self, practica: Practica) -> Practica:
        pass

    @abstractmethod
    def obtener_por_id(self, practica_id: int) -> Optional[Practica]:
        pass

    @abstractmethod
    def obtener_por_postulacion(self, postulacion_id: int) -> Optional[Practica]:
        pass

    @abstractmethod
    def obtener_por_practicante(self, practicante_id: int) -> List[Practica]:
        pass

    @abstractmethod
    def obtener_por_empresa(self, empresa_id: int) -> List[Practica]:
        pass

    @abstractmethod
    def actualizar(self, practica: Practica) -> Practica:
        pass