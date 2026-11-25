from internships.domain.deliverable import Deliverable
from internships.domain.evaluation import Evaluation
from shared.errors import ConflictError, DomainError, NotFoundError


class Internship:
    STATUS_IN_PROGRESS = "EN_CURSO"
    STATUS_FINISHED = "FINALIZADA"

    def __init__(self, id=None, job_application_id=None, intern_id=None,
                 status=None, deliverables=None, evaluations=None):
        self.id = id
        self.job_application_id = job_application_id
        self.intern_id = intern_id
        self.status = status or self.STATUS_IN_PROGRESS
        self.deliverables = deliverables or []
        self.evaluations = evaluations or []

    @classmethod
    def start(cls, job_application_id, intern_id):
        if job_application_id is None or intern_id is None:
            raise DomainError("Se requiere postulación y practicante para iniciar la práctica")
        return cls(
            job_application_id=job_application_id,
            intern_id=intern_id,
            status=cls.STATUS_IN_PROGRESS,
        )

    def upload_deliverable(self, file_name):
        if self.status == self.STATUS_FINISHED:
            raise ConflictError("No se pueden subir entregables a una práctica finalizada")

        deliverable = Deliverable.create(internship_id=self.id, file_name=file_name)
        self.deliverables.append(deliverable)
        return deliverable

    def register_evaluation(self, score):
        if self.status == self.STATUS_FINISHED:
            raise ConflictError("No se pueden registrar evaluaciones en una práctica finalizada")

        evaluation = Evaluation.create(internship_id=self.id, score=score)
        self.evaluations.append(evaluation)
        return evaluation

    def remove_deliverable(self, deliverable_id):
        if self.status != self.STATUS_IN_PROGRESS:
            raise ConflictError("No se pueden eliminar entregables de una práctica finalizada")
        deliverable = next(
            (item for item in self.deliverables if item.id == deliverable_id),
            None,
        )
        if deliverable is None:
            raise NotFoundError("Entregable no encontrado")
        self.deliverables.remove(deliverable)
        return deliverable

    def remove_evaluation(self, evaluation_id):
        if self.status != self.STATUS_IN_PROGRESS:
            raise ConflictError("No se pueden eliminar evaluaciones de una práctica finalizada")
        evaluation = next(
            (item for item in self.evaluations if item.id == evaluation_id),
            None,
        )
        if evaluation is None:
            raise NotFoundError("Evaluación no encontrada")
        self.evaluations.remove(evaluation)
        return evaluation

    def finish(self):
        if self.status != self.STATUS_IN_PROGRESS:
            raise ConflictError("La práctica ya está finalizada")
        if not self.deliverables:
            raise ConflictError("No se puede finalizar una práctica sin entregables registrados")
        if not any(evaluation.is_approved() for evaluation in self.evaluations):
            raise ConflictError(
                "No se puede finalizar una práctica sin una evaluación aprobada"
            )

        self.status = self.STATUS_FINISHED
        return self

    def get_deliverables_history(self):
        return sorted(self.deliverables, key=lambda e: e.uploaded_at)

    def get_evaluations_history(self):
        return sorted(self.evaluations, key=lambda e: e.evaluated_at)
