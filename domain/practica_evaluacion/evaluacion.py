# domain/practica_evaluacion/evaluacion.py
from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict, Any, Optional

@dataclass
class Evaluacion:
    """Entidad que representa una evaluación de entregable."""
    id: Optional[int]
    entregable_id: int
    puntaje: float
    comentario: str
    criterios_evaluacion: List[Dict[str, Any]]
    fecha_evaluacion: Optional[datetime] = None

    def __post_init__(self):
        if self.fecha_evaluacion is None:
            self.fecha_evaluacion = datetime.utcnow()
        if self.criterios_evaluacion is None:
            self.criterios_evaluacion = []

    def es_aprobatoria(self) -> bool:
        """Verifica si la evaluación es aprobatoria (puntaje >= 4.0)."""
        return self.puntaje >= 4.0

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "entregable_id": self.entregable_id,
            "puntaje": self.puntaje,
            "comentario": self.comentario,
            "criterios_evaluacion": self.criterios_evaluacion,
            "fecha_evaluacion": self.fecha_evaluacion.isoformat() if self.fecha_evaluacion else None
        }