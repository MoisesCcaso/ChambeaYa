from datetime import datetime, timezone
from shared.errors import DomainError

PASSING_SCORE = 60.0


class Evaluation:
    def __init__(self, id=None, internship_id=None, score=None, evaluated_at=None):
        self.id = id
        self.internship_id = internship_id
        self.score = score
        self.evaluated_at = evaluated_at

    @staticmethod
    def create(internship_id, score):
        if score is None:
            raise DomainError("Debe indicarse un puntaje")
        try:
            score = float(score)
        except (TypeError, ValueError) as exc:
            raise DomainError("El puntaje debe ser numérico") from exc
        if score < 0 or score > 100:
            raise DomainError("El puntaje debe estar entre 0 y 100")

        return Evaluation(
            internship_id=internship_id,
            score=score,
            evaluated_at= datetime.now(timezone.utc),
        )

    def is_approved(self):
        if self.score is None:
            return False
        return self.score >= PASSING_SCORE
