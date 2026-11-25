from typing import Final

from recruitment.domain.convocatoria import Convocatoria
from recruitment.domain.postulacion import Postulacion
from shared.error_messages import JOB_POSTING_NOT_FOUND, JOB_APPLICATION_NOT_FOUND
from recruitment.application.dtos import CandidatoConvocatoriaDTO, PostulacionDetalleDTO
from shared.errors import ConflictError, ForbiddenError, NotFoundError

NOT_FOUND_PRACTICANTE: Final = "Perfil de practicante no encontrado"


class PostulacionApplicationService:
    def __init__(
        self,
        postulacion_repository=None,
        convocatoria_repository=None,
        profile_repository=None,
        practica_repository=None,
        intern_repository=None,
        notification_service=None,
    ):
        self.postulacion_repository = postulacion_repository
        self.convocatoria_repository = convocatoria_repository
        self.intern_repository = intern_repository or profile_repository
        self.profile_repository = self.intern_repository
        self.practica_repository = practica_repository
        self.notification_service = notification_service

    def apply(self, user_id, convocatoria_id):
        self._require_repositories()
        intern = self.profile_repository.find_intern_by_user_id(user_id)
        if intern is None:
            raise ForbiddenError(NOT_FOUND_PRACTICANTE)
        if not intern.first_names or not intern.last_names:
            raise ConflictError("Completa tus nombres y apellidos antes de postular")

        convocatoria = self.convocatoria_repository.find_by_id(convocatoria_id)
        if convocatoria is None:
            raise NotFoundError(JOB_POSTING_NOT_FOUND)
        if convocatoria.status != Convocatoria.ESTADO_PUBLICADA:
            raise ConflictError("Solo se puede postular a convocatorias publicadas")

        existing = self.postulacion_repository.find_by_convocatoria_and_practicante(
            convocatoria_id, intern.id
        )
        if existing is not None:
            if existing.status == Postulacion.ESTADO_CANCELADA:
                existing.reactivar()
                return self.postulacion_repository.save(existing)
            raise ConflictError("Ya existe una postulación para esta convocatoria")

        return self.postulacion_repository.save(
            Postulacion(
                convocatoria_id=convocatoria_id,
                intern_id=intern.id,
            )
        )

    def list_for_practicante(self, user_id):
        self._require_repositories()
        intern = self.profile_repository.find_intern_by_user_id(user_id)
        if intern is None:
            raise ForbiddenError(NOT_FOUND_PRACTICANTE)
        return [
            PostulacionDetalleDTO(
                postulacion,
                self.convocatoria_repository.find_by_id(postulacion.convocatoria_id),
            )
            for postulacion in self.postulacion_repository.find_by_practicante_id(
                intern.id
            )
        ]

    def list_for_convocatoria(self, company_id, convocatoria_id):
        self._require_repositories()
        self._require_owned_convocatoria(company_id, convocatoria_id)
        return [
            CandidatoConvocatoriaDTO(
                postulacion,
                self.profile_repository.find_intern_by_id(postulacion.intern_id),
                self.practica_repository.find_by_postulacion_id(postulacion.id),
            )
            for postulacion in self.postulacion_repository.find_by_convocatoria_id(
                convocatoria_id
            )
        ]

    def select_candidate(self, company_id, postulacion_id):
        self._require_repositories()
        postulacion = self.postulacion_repository.find_by_id(postulacion_id)
        if postulacion is None:
            raise NotFoundError(JOB_APPLICATION_NOT_FOUND)
        convocatoria = self.convocatoria_repository.find_by_id(postulacion.convocatoria_id)
        if convocatoria is None:
            raise NotFoundError(JOB_POSTING_NOT_FOUND)
        if convocatoria.company_id != company_id:
            raise ForbiddenError("La convocatoria no pertenece a esta empresa")

        otras = self.postulacion_repository.find_by_convocatoria_id(
            postulacion.convocatoria_id
        )
        for otra in otras:
            if (
                otra.id != postulacion.id
                and otra.status == Postulacion.ESTADO_SELECCIONADA
                and self.practica_repository.find_by_postulacion_id(otra.id) is not None
            ):
                raise ConflictError(
                    "No se puede cambiar al candidato porque la práctica seleccionada ya inició"
                )

        postulacion.seleccionar()
        modificadas = [postulacion]
        rechazadas = []
        for otra in otras:
            if otra.id == postulacion.id:
                continue
            if otra.status == Postulacion.STATUS_PENDING:
                otra.rechazar()
                modificadas.append(otra)
                rechazadas.append(otra)
            elif otra.status == Postulacion.ESTADO_SELECCIONADA:
                otra.rechazar_seleccionada()
                modificadas.append(otra)
                rechazadas.append(otra)
        guardadas = self.postulacion_repository.save_all(modificadas)
        seleccionada = guardadas[0]
        self._notificar_seleccion(seleccionada, rechazadas)
        return seleccionada


    def _notificar_seleccion(self, seleccionada, rechazadas):
        if self.notification_service is None or self.profile_repository is None:
            return
        try:
            intern = self.profile_repository.find_intern_by_id(seleccionada.intern_id)
            if intern and getattr(intern, "user_id", None):
                self.notification_service.create_notification(
                    recipient_user_id=intern.user_id,
                    notification_type="POSTULACION_SELECCIONADA",
                    message="Has sido seleccionado para una convocatoria",
                    metadata={"postulacion_id": seleccionada.id},
                )
            for rechazada in rechazadas:
                otro = self.profile_repository.find_intern_by_id(rechazada.intern_id)
                if otro and getattr(otro, "user_id", None):
                    self.notification_service.create_notification(
                        recipient_user_id=otro.user_id,
                        notification_type="POSTULACION_RECHAZADA",
                        message="Tu postulación no fue seleccionada",
                        metadata={"postulacion_id": rechazada.id},
                    )
        except Exception:
            pass

    def reject_candidate(self, company_id, postulacion_id):
        self._require_repositories()
        postulacion = self.postulacion_repository.find_by_id(postulacion_id)
        if postulacion is None:
            raise NotFoundError(JOB_APPLICATION_NOT_FOUND)
        self._require_owned_convocatoria(company_id, postulacion.convocatoria_id)
        postulacion.rechazar()
        return self.postulacion_repository.save(postulacion)

    def cancel(self, user_id, postulacion_id):
        self._require_repositories()
        intern = self.profile_repository.find_intern_by_user_id(user_id)
        if intern is None:
            raise ForbiddenError(NOT_FOUND_PRACTICANTE)
        postulacion = self.postulacion_repository.find_by_id(postulacion_id)
        if postulacion is None:
            raise NotFoundError(JOB_APPLICATION_NOT_FOUND)
        if postulacion.intern_id != intern.id:
            raise ForbiddenError("La postulación no pertenece a este practicante")
        postulacion.cancelar()
        return self.postulacion_repository.save(postulacion)

    def reconsider_candidate(self, company_id, postulacion_id):
        self._require_repositories()
        postulacion = self.postulacion_repository.find_by_id(postulacion_id)
        if postulacion is None:
            raise NotFoundError(JOB_APPLICATION_NOT_FOUND)
        self._require_owned_convocatoria(company_id, postulacion.convocatoria_id)
        if self.practica_repository.find_by_postulacion_id(postulacion.id) is not None:
            raise ConflictError(
                "No se puede cambiar la decisión porque la práctica ya fue iniciada"
            )
        postulacion.reconsiderar()
        return self.postulacion_repository.save(postulacion)

    def _require_owned_convocatoria(self, company_id, convocatoria_id):
        convocatoria = self.convocatoria_repository.find_by_id(convocatoria_id)
        if convocatoria is None:
            raise NotFoundError(JOB_POSTING_NOT_FOUND)
        if convocatoria.company_id != company_id:
            raise ForbiddenError("La convocatoria no pertenece a esta empresa")
        return convocatoria

    def _require_repositories(self):
        if (
            self.postulacion_repository is None
            or self.convocatoria_repository is None
            or self.profile_repository is None
            or self.practica_repository is None
        ):
            raise RuntimeError("PostulacionApplicationService requiere todos sus repositorios")
