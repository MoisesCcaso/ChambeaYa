from abc import ABC, abstractmethod


class MatchingStrategy(ABC):
    """Define el algoritmo para calcular compatibilidad entre habilidades."""

    @abstractmethod
    def calcular_compatibilidad(self, habilidades_practicante, required_skills):
        """Retorna el puntaje y las habilidades coincidentes."""
        raise NotImplementedError
