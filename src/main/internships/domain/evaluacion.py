from datetime import datetime, timezone
from shared.errors import DomainError

PUNTAJE_APROBACION = 60.0


class Evaluacion:
    def __init__(self, id=None, practica_id=None, score=None, fecha_evaluacion=None):
        self.id = id
        self.practica_id = practica_id
        self.score = score
        self.fecha_evaluacion = fecha_evaluacion

    @staticmethod
    def crear(practica_id, score):
        if score is None:
            raise DomainError("Debe indicarse un puntaje")
        try:
            score = float(score)
        except (TypeError, ValueError) as exc:
            raise DomainError("El puntaje debe ser numérico") from exc
        if score < 0 or score > 100:
            raise DomainError("El puntaje debe estar entre 0 y 100")

        return Evaluacion(
            practica_id=practica_id,
            score=score,
            fecha_evaluacion= datetime.now(timezone.utc),
        )

    def esta_aprobada(self):
        if self.score is None:
            return False
        return self.score >= PUNTAJE_APROBACION
