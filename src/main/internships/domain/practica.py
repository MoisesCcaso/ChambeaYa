from internships.domain.entregable import Entregable
from internships.domain.evaluacion import Evaluacion
from shared.errors import ConflictError, DomainError, NotFoundError


class Practica:
    ESTADO_EN_CURSO = "EN_CURSO"
    ESTADO_FINALIZADA = "FINALIZADA"

    def __init__(self, id=None, job_application_id=None, intern_id=None,
                 status=None, entregables=None, evaluaciones=None):
        self.id = id
        self.job_application_id = job_application_id
        self.intern_id = intern_id
        self.status = status or self.ESTADO_EN_CURSO
        self.entregables = entregables or []
        self.evaluaciones = evaluaciones or []

    @classmethod
    def iniciar(cls, job_application_id, intern_id):
        if job_application_id is None or intern_id is None:
            raise DomainError("Se requiere postulación y practicante para iniciar la práctica")
        return cls(
            job_application_id=job_application_id,
            intern_id=intern_id,
            status=cls.ESTADO_EN_CURSO,
        )

    def subir_entregable(self, archivo):
        if self.status == self.ESTADO_FINALIZADA:
            raise ConflictError("No se pueden subir entregables a una práctica finalizada")

        entregable = Entregable.crear(practica_id=self.id, archivo=archivo)
        self.entregables.append(entregable)
        return entregable

    def registrar_evaluacion(self, score):
        if self.status == self.ESTADO_FINALIZADA:
            raise ConflictError("No se pueden registrar evaluaciones en una práctica finalizada")

        evaluacion = Evaluacion.crear(practica_id=self.id, score=score)
        self.evaluaciones.append(evaluacion)
        return evaluacion

    def eliminar_entregable(self, entregable_id):
        if self.status != self.ESTADO_EN_CURSO:
            raise ConflictError("No se pueden eliminar entregables de una práctica finalizada")
        entregable = next(
            (item for item in self.entregables if item.id == entregable_id),
            None,
        )
        if entregable is None:
            raise NotFoundError("Entregable no encontrado")
        self.entregables.remove(entregable)
        return entregable

    def eliminar_evaluacion(self, evaluacion_id):
        if self.status != self.ESTADO_EN_CURSO:
            raise ConflictError("No se pueden eliminar evaluaciones de una práctica finalizada")
        evaluacion = next(
            (item for item in self.evaluaciones if item.id == evaluacion_id),
            None,
        )
        if evaluacion is None:
            raise NotFoundError("Evaluación no encontrada")
        self.evaluaciones.remove(evaluacion)
        return evaluacion

    def finalizar(self):
        if self.status != self.ESTADO_EN_CURSO:
            raise ConflictError("La práctica ya está finalizada")
        if not self.entregables:
            raise ConflictError("No se puede finalizar una práctica sin entregables registrados")
        if not any(evaluacion.esta_aprobada() for evaluacion in self.evaluaciones):
            raise ConflictError(
                "No se puede finalizar una práctica sin una evaluación aprobada"
            )

        self.status = self.ESTADO_FINALIZADA
        return self

    def obtener_historial_entregables(self):
        return sorted(self.entregables, key=lambda e: e.fecha_subida)

    def obtener_historial_evaluaciones(self):
        return sorted(self.evaluaciones, key=lambda e: e.fecha_evaluacion)
