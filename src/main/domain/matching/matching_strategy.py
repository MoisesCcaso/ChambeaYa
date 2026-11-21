from abc import ABC, abstractmethod


class MatchingStrategy(ABC):
    """Define el algoritmo para calcular compatibilidad entre habilidades."""

    @abstractmethod
    def calcular_compatibilidad(self, habilidades_practicante, habilidades_requeridas):
        """Retorna el puntaje y las habilidades coincidentes."""
        raise NotImplementedError
