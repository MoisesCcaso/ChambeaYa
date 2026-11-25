from domain.practica_evaluacion.entregable import Entregable
from domain.practica_evaluacion.evaluacion import Evaluacion
from shared.errors import ConflictError, DomainError, NotFoundError


class Practica:
    ESTADO_EN_CURSO = "EN_CURSO"
    ESTADO_FINALIZADA = "FINALIZADA"

    def __init__(self, id=None, postulacion_id=None, practicante_id=None,
                 status=None, entregables=None, evaluaciones=None):
        self.id = id
        self.postulacion_id = postulacion_id
        self.practicante_id = practicante_id
        self.status = status or self.ESTADO_EN_CURSO
        self.entregables = entregables or []
        self.evaluaciones = evaluaciones or []

    @classmethod
    def iniciar(cls, postulacion_id, practicante_id):
        if postulacion_id is None or practicante_id is None:
            raise DomainError("Se requiere postulación y practicante para iniciar la práctica")
        return cls(
            postulacion_id=postulacion_id,
            practicante_id=practicante_id,
            status=cls.ESTADO_EN_CURSO,
        )

    def subir_entregable(self, archivo):
        if self.status == self.ESTADO_FINALIZADA:
            raise ConflictError("No se pueden subir entregables a una práctica finalizada")

        entregable = Entregable.crear(practica_id=self.id, archivo=archivo)
        self.entregables.append(entregable)
        return entregable

    def registrar_evaluacion(self, puntaje):
        if self.status == self.ESTADO_FINALIZADA:
            raise ConflictError("No se pueden registrar evaluaciones en una práctica finalizada")

        evaluacion = Evaluacion.crear(practica_id=self.id, puntaje=puntaje)
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
