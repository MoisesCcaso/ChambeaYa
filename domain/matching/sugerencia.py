# domain/matching/sugerencia.py
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

@dataclass
class Sugerencia:
    """Entidad que representa una sugerencia de matching."""
    id: Optional[int]
    convocatoria_id: int
    practicante_id: int
    score_match: float
    habilidades_match: List[str]
    fecha_generacion: Optional[datetime] = None

    def __post_init__(self):
        if self.fecha_generacion is None:
            self.fecha_generacion = datetime.utcnow()
        if self.habilidades_match is None:
            self.habilidades_match = []

    def es_relevante(self, umbral: float = 0.3) -> bool:
        """Verifica si la sugerencia es relevante (score mayor al umbral)."""
        return self.score_match >= umbral

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "convocatoria_id": self.convocatoria_id,
            "practicante_id": self.practicante_id,
            "score_match": self.score_match,
            "habilidades_match": self.habilidades_match,
            "fecha_generacion": self.fecha_generacion.isoformat() if self.fecha_generacion else None
        }