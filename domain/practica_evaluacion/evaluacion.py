# domain/practica_evaluacion/evaluacion.py
# LAB 12 - SOLID: O (Abierto/Cerrado)
# La clase base está abierta para extensión (herencia) pero cerrada para modificación.

from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod


@dataclass
class Evaluacion(ABC):
    """
    Clase base abstracta para evaluaciones.
    Está ABIERTA para extensión (puedes crear nuevas subclases) pero
    CERRADA para modificación (no debes cambiar esta clase base).
    """
    id: Optional[int]
    entregable_id: int
    puntaje: float
    comentario: str
    fecha_evaluacion: Optional[datetime] = None

    def __post_init__(self):
        if self.fecha_evaluacion is None:
            self.fecha_evaluacion = datetime.utcnow()

    @abstractmethod
    def es_aprobatoria(self) -> bool:
        """
        Método abstracto que las subclases deben implementar.
        Permite diferentes criterios de aprobación según el tipo de evaluación.
        """
        pass

    @abstractmethod
    def obtener_puntaje_normalizado(self) -> float:
        """
        Método abstracto para normalizar puntajes según diferentes escalas.
        """
        pass

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "entregable_id": self.entregable_id,
            "puntaje": self.puntaje,
            "comentario": self.comentario,
            "fecha_evaluacion": self.fecha_evaluacion.isoformat() if self.fecha_evaluacion else None
        }


# Ejemplo de extensión (nueva subclase)
@dataclass
class EvaluacionTecnica(Evaluacion):
    """
    Subclase que extiende Evaluacion para evaluaciones técnicas.
    No modifica la clase base, solo la extiende.
    """
    criterios_tecnicos: List[str] = None

    def es_aprobatoria(self) -> bool:
        # Criterio de aprobación: puntaje >= 4.0
        return self.puntaje >= 4.0

    def obtener_puntaje_normalizado(self) -> float:
        # Normaliza a escala 0-1
        return self.puntaje / 5.0


@dataclass
class EvaluacionFinal(Evaluacion):
    """
    Subclase que extiende Evaluacion para evaluaciones finales de práctica.
    """
    def es_aprobatoria(self) -> bool:
        # Criterio de aprobación: puntaje >= 3.5
        return self.puntaje >= 3.5

    def obtener_puntaje_normalizado(self) -> float:
        # Normaliza a escala 0-100
        return self.puntaje * 20