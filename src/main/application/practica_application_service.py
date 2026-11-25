from typing import Final

from recruitment.domain.postulacion import Postulacion
from domain.practica_evaluacion.practica import Practica
from shared.error_messages import JOB_POSTING_NOT_FOUND, JOB_APPLICATION_NOT_FOUND
from shared.errors import ConflictError, ForbiddenError, NotFoundError

NOT_FOUND: Final = "Práctica no encontrada"


class PracticaApplicationService:
    def __init__(self, practica_repository=None, profile_repository=None, postulacion_repository=None, convocatoria_repository=None, notification_service=None):
        self.practica_repository = practica_repository
        self.profile_repository = profile_repository
        self.postulacion_repository = postulacion_repository
        self.convocatoria_repository = convocatoria_repository
        self.notification_service = notification_service

    def start_practica(self, company_id, postulacion_id):
        self._require_repositories()
        postulacion = self.postulacion_repository.find_by_id(postulacion_id)
        if postulacion is None:
            raise NotFoundError(JOB_APPLICATION_NOT_FOUND)
        if postulacion.status != Postulacion.ESTADO_SELECCIONADA:
            raise ConflictError("La postulación debe estar seleccionada para iniciar la práctica")

        convocatoria = self.convocatoria_repository.find_by_id(postulacion.convocatoria_id)
        if convocatoria is None:
            raise NotFoundError(JOB_POSTING_NOT_FOUND)
        if convocatoria.company_id != company_id:
            raise ForbiddenError("La postulación no pertenece a esta empresa")

        existing = self.practica_repository.find_by_postulacion_id(postulacion_id)
        if existing is not None:
            raise ConflictError("La práctica ya fue iniciada")

        practica = Practica.iniciar(postulacion_id, postulacion.intern_id)
        return self.practica_repository.save(practica)

    def upload_deliverable(self, user_id, practica_id, archivo):
        self._require_repositories()
        practica = self._get_practica_autorizada(user_id, practica_id)
        practica.subir_entregable(archivo)
        return self.practica_repository.save(practica)

    def get_deliverables_history(self, user_id, practica_id):
        self._require_repositories()
        practica = self._get_practica_visible(user_id, practica_id)
        return practica.obtener_historial_entregables()

    def delete_deliverable(self, user_id, practica_id, entregable_id):
        self._require_repositories()
        practica = self._get_practica_autorizada(user_id, practica_id)
        eliminado = practica.eliminar_entregable(entregable_id)
        self.practica_repository.save(practica)
        return eliminado

    def evaluate(self, company_id, practica_id, puntaje):
        self._require_repositories()
        practica = self.practica_repository.find_by_id(practica_id)
        if practica is None:
            raise NotFoundError(NOT_FOUND)
        postulacion = self.postulacion_repository.find_by_id(practica.postulacion_id)
        if postulacion is None:
            raise NotFoundError(JOB_APPLICATION_NOT_FOUND)

        convocatoria = self.convocatoria_repository.find_by_id(postulacion.convocatoria_id)
        if convocatoria is None:
            raise NotFoundError(JOB_POSTING_NOT_FOUND)
        if convocatoria.company_id != company_id:
            raise ForbiddenError("La práctica no pertenece a una convocatoria de esta empresa")

        practica.registrar_evaluacion(puntaje)
        saved = self.practica_repository.save(practica)
        self._notificar_evaluacion(saved)
        return saved

    def _notificar_evaluacion(self, practica):
        if self.notification_service is None or self.profile_repository is None:
            return
        intern_id = getattr(practica, "intern_id", None)
        if not intern_id:
            return
        try:
            intern = self.profile_repository.find_intern_by_id(intern_id)
            user_id = getattr(intern, "user_id", None)
            if user_id:
                self.notification_service.create_notification(
                    recipient_user_id=user_id,
                    notification_type="EVALUACION_DISPONIBLE",
                    message="Tu práctica tiene una nueva evaluación disponible",
                    metadata={"practica_id": practica.id},
                )
        except Exception:
            pass

    def get_evaluations_history(self, user_id, practica_id):
        self._require_repositories()
        practica = self._get_practica_visible(user_id, practica_id)
        return practica.obtener_historial_evaluaciones()

    def delete_evaluation(self, company_id, practica_id, evaluacion_id):
        self._require_repositories()
        practica = self.practica_repository.find_by_id(practica_id)
        if practica is None:
            raise NotFoundError(NOT_FOUND)
        self._require_empresa_owner(company_id, practica)
        eliminada = practica.eliminar_evaluacion(evaluacion_id)
        self.practica_repository.save(practica)
        return eliminada

    def finish(self, company_id, practica_id):
        self._require_repositories()
        practica = self.practica_repository.find_by_id(practica_id)
        if practica is None:
            raise NotFoundError(NOT_FOUND)
        self._require_empresa_owner(company_id, practica)

        practica.finalizar()
        return self.practica_repository.save(practica)

    def list_for_user(self, user_id):
        self._require_repositories()
        intern = self.profile_repository.find_intern_by_user_id(user_id)
        if intern is not None:
            return self.practica_repository.find_by_practicante_id(intern.id)

        company = self.profile_repository.find_company_by_user_id(user_id)
        if company is None:
            raise NotFoundError("Perfil no encontrado")

        if hasattr(self.practica_repository, "find_by_empresa_id"):
            return self.practica_repository.find_by_empresa_id(company.id)

        practicas = []
        for convocatoria in self.convocatoria_repository.find_by_empresa_id(company.id):
            for postulacion in self.postulacion_repository.find_by_convocatoria_id(
                convocatoria.id
            ):
                practica = self.practica_repository.find_by_postulacion_id(postulacion.id)
                if practica is not None:
                    practicas.append(practica)
        return practicas

    def get_for_user(self, user_id, practica_id):
        self._require_repositories()
        return self._get_practica_visible(user_id, practica_id)

    def _get_practica_autorizada(self, user_id, practica_id):
        intern = self.profile_repository.find_intern_by_user_id(user_id)
        if intern is None:
            raise ForbiddenError("Perfil de practicante no encontrado")

        practica = self.practica_repository.find_by_id(practica_id)
        if practica is None:
            raise NotFoundError(NOT_FOUND)

        if practica.intern_id != intern.id:
            raise ForbiddenError("No autorizado para acceder a esta práctica")

        return practica

    def _get_practica_visible(self, user_id, practica_id):
        practica = self.practica_repository.find_by_id(practica_id)
        if practica is None:
            raise NotFoundError(NOT_FOUND)

        intern = self.profile_repository.find_intern_by_user_id(user_id)
        if intern is not None and practica.intern_id == intern.id:
            return practica

        company = self.profile_repository.find_company_by_user_id(user_id)
        if company is not None:
            self._require_empresa_owner(company.id, practica)
            return practica

        raise ForbiddenError("No autorizado para acceder a esta práctica")

    def _require_empresa_owner(self, company_id, practica):
        postulacion = self.postulacion_repository.find_by_id(practica.postulacion_id)
        if postulacion is None:
            raise NotFoundError(JOB_APPLICATION_NOT_FOUND)
        convocatoria = self.convocatoria_repository.find_by_id(postulacion.convocatoria_id)
        if convocatoria is None:
            raise NotFoundError(JOB_POSTING_NOT_FOUND)
        if convocatoria.company_id != company_id:
            raise ForbiddenError("La práctica no pertenece a esta empresa")
        return convocatoria

    def _require_repositories(self):
        if any(
            repository is None
            for repository in (
                self.practica_repository,
                self.profile_repository,
                self.postulacion_repository,
                self.convocatoria_repository,
            )
        ):
            raise RuntimeError("PracticaApplicationService requiere todos sus repositorios")
