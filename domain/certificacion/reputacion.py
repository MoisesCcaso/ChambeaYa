# domain/certificacion/reputacion.py
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Reputacion:
    """Entidad que representa la reputación de un usuario."""
    id: Optional[int]
    usuario_id: int
    score_total: float
    evaluaciones_count: int
    practicas_completadas: int
    promedio_puntaje: float
    ultima_actualizacion: datetime

    def __post_init__(self):
        if self.ultima_actualizacion is None:
            self.ultima_actualizacion = datetime.utcnow()
        if self.score_total is None:
            self.score_total = 0.0
        if self.evaluaciones_count is None:
            self.evaluaciones_count = 0
        if self.practicas_completadas is None:
            self.practicas_completadas = 0
        if self.promedio_puntaje is None:
            self.promedio_puntaje = 0.0

    def actualizar(self, nuevo_puntaje: float) -> None:
        """Actualiza la reputación con un nuevo puntaje de evaluación."""
        self.evaluaciones_count += 1
        self.promedio_puntaje = ((self.promedio_puntaje * (self.evaluaciones_count - 1)) + nuevo_puntaje) / self.evaluaciones_count
        self.score_total = self._calcular_score()
        self.ultima_actualizacion = datetime.utcnow()

    def incrementar_practicas_completadas(self) -> None:
        """Incrementa el contador de prácticas completadas."""
        self.practicas_completadas += 1
        self.score_total = self._calcular_score()
        self.ultima_actualizacion = datetime.utcnow()

    def _calcular_score(self) -> float:
        """Calcula el score total basado en promedio y prácticas completadas."""
        if self.practicas_completadas == 0:
            return 0.0
        # Fórmula: promedio * (1 + 0.1 * prácticas_completadas)
        return round(self.promedio_puntaje * (1 + 0.1 * self.practicas_completadas), 2)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "usuario_id": self.usuario_id,
            "score_total": self.score_total,
            "evaluaciones_count": self.evaluaciones_count,
            "practicas_completadas": self.practicas_completadas,
            "promedio_puntaje": self.promedio_puntaje,
            "ultima_actualizacion": self.ultima_actualizacion.isoformat() if self.ultima_actualizacion else None
        }