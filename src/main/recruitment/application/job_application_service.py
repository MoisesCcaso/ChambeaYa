from typing import Final

from recruitment.domain.job_posting import JobPosting
from recruitment.domain.job_application import JobApplication
from shared.error_messages import JOB_POSTING_NOT_FOUND, JOB_APPLICATION_NOT_FOUND
from recruitment.application.dtos import CandidateDTO, JobApplicationDetailDTO
from shared.errors import ConflictError, ForbiddenError, NotFoundError

INTERN_PROFILE_NOT_FOUND: Final = "Perfil de practicante no encontrado"


class JobApplicationService:
    def __init__(
        self,
        job_application_repository=None,
        job_posting_repository=None,
        profile_repository=None,
        practica_repository=None,
        intern_repository=None,
        notification_service=None,
    ):
        self.job_application_repository = job_application_repository
        self.job_posting_repository = job_posting_repository
        self.intern_repository = intern_repository or profile_repository
        self.profile_repository = self.intern_repository
        self.practica_repository = practica_repository
        self.notification_service = notification_service

    def apply(self, user_id, job_posting_id):
        self._require_repositories()
        intern = self.profile_repository.find_intern_by_user_id(user_id)
        if intern is None:
            raise ForbiddenError(INTERN_PROFILE_NOT_FOUND)
        if not intern.first_names or not intern.last_names:
            raise ConflictError("Completa tus nombres y apellidos antes de postular")

        job_posting = self.job_posting_repository.find_by_id(job_posting_id)
        if job_posting is None:
            raise NotFoundError(JOB_POSTING_NOT_FOUND)
        if job_posting.status != JobPosting.STATUS_PUBLISHED:
            raise ConflictError("Solo se puede postular a convocatorias publicadas")

        existing = self.job_application_repository.find_by_job_posting_and_intern(
            job_posting_id, intern.id
        )
        if existing is not None:
            if existing.status == JobApplication.STATUS_CANCELLED:
                existing.reactivate()
                return self.job_application_repository.save(existing)
            raise ConflictError("Ya existe una postulación para esta convocatoria")

        return self.job_application_repository.save(
            JobApplication(
                job_posting_id=job_posting_id,
                intern_id=intern.id,
            )
        )

    def list_for_intern(self, user_id):
        self._require_repositories()
        intern = self.profile_repository.find_intern_by_user_id(user_id)
        if intern is None:
            raise ForbiddenError(INTERN_PROFILE_NOT_FOUND)
        return [
            JobApplicationDetailDTO(
                job_application,
                self.job_posting_repository.find_by_id(job_application.job_posting_id),
            )
            for job_application in self.job_application_repository.find_by_intern_id(
                intern.id
            )
        ]

    def list_for_job_posting(self, company_id, job_posting_id):
        self._require_repositories()
        self._require_owned_job_posting(company_id, job_posting_id)
        return [
            CandidateDTO(
                job_application,
                self.profile_repository.find_intern_by_id(job_application.intern_id),
                self.practica_repository.find_by_job_application_id(job_application.id),
            )
            for job_application in self.job_application_repository.find_by_job_posting_id(
                job_posting_id
            )
        ]

    def select_candidate(self, company_id, job_application_id):
        self._require_repositories()
        job_application = self.job_application_repository.find_by_id(job_application_id)
        if job_application is None:
            raise NotFoundError(JOB_APPLICATION_NOT_FOUND)
        job_posting = self.job_posting_repository.find_by_id(job_application.job_posting_id)
        if job_posting is None:
            raise NotFoundError(JOB_POSTING_NOT_FOUND)
        if job_posting.company_id != company_id:
            raise ForbiddenError("La convocatoria no pertenece a esta empresa")

        others = self.job_application_repository.find_by_job_posting_id(
            job_application.job_posting_id
        )
        for other in others:
            if (
                other.id != job_application.id
                and other.status == JobApplication.STATUS_SELECTED
                and self.practica_repository.find_by_job_application_id(other.id) is not None
            ):
                raise ConflictError(
                    "No se puede cambiar al candidato porque la práctica seleccionada ya inició"
                )

        job_application.select()
        modified = [job_application]
        rejected_ones = []
        for other in others:
            if other.id == job_application.id:
                continue
            if other.status == JobApplication.STATUS_PENDING:
                other.reject()
                modified.append(other)
                rejected_ones.append(other)
            elif other.status == JobApplication.STATUS_SELECTED:
                other.reject_selected()
                modified.append(other)
                rejected_ones.append(other)
        saved_items = self.job_application_repository.save_all(modified)
        selected = saved_items[0]
        self._notify_selection(selected, rejected_ones)
        return selected


    def _notify_selection(self, selected, rejected_ones):
        if self.notification_service is None or self.profile_repository is None:
            return
        try:
            intern = self.profile_repository.find_intern_by_id(selected.intern_id)
            if intern and getattr(intern, "user_id", None):
                self.notification_service.create_notification(
                    recipient_user_id=intern.user_id,
                    notification_type="POSTULACION_SELECCIONADA",
                    message="Has sido seleccionado para una convocatoria",
                    metadata={"postulacion_id": selected.id},
                )
            for rejected in rejected_ones:
                other_intern = self.profile_repository.find_intern_by_id(rejected.intern_id)
                if other_intern and getattr(other_intern, "user_id", None):
                    self.notification_service.create_notification(
                        recipient_user_id=other_intern.user_id,
                        notification_type="POSTULACION_RECHAZADA",
                        message="Tu postulación no fue seleccionada",
                        metadata={"postulacion_id": rejected.id},
                    )
        except Exception:
            pass

    def reject_candidate(self, company_id, job_application_id):
        self._require_repositories()
        job_application = self.job_application_repository.find_by_id(job_application_id)
        if job_application is None:
            raise NotFoundError(JOB_APPLICATION_NOT_FOUND)
        self._require_owned_job_posting(company_id, job_application.job_posting_id)
        job_application.reject()
        return self.job_application_repository.save(job_application)

    def cancel(self, user_id, job_application_id):
        self._require_repositories()
        intern = self.profile_repository.find_intern_by_user_id(user_id)
        if intern is None:
            raise ForbiddenError(INTERN_PROFILE_NOT_FOUND)
        job_application = self.job_application_repository.find_by_id(job_application_id)
        if job_application is None:
            raise NotFoundError(JOB_APPLICATION_NOT_FOUND)
        if job_application.intern_id != intern.id:
            raise ForbiddenError("La postulación no pertenece a este practicante")
        job_application.cancel()
        return self.job_application_repository.save(job_application)

    def reconsider_candidate(self, company_id, job_application_id):
        self._require_repositories()
        job_application = self.job_application_repository.find_by_id(job_application_id)
        if job_application is None:
            raise NotFoundError(JOB_APPLICATION_NOT_FOUND)
        self._require_owned_job_posting(company_id, job_application.job_posting_id)
        if self.practica_repository.find_by_job_application_id(job_application.id) is not None:
            raise ConflictError(
                "No se puede cambiar la decisión porque la práctica ya fue iniciada"
            )
        job_application.reconsider()
        return self.job_application_repository.save(job_application)

    def _require_owned_job_posting(self, company_id, job_posting_id):
        job_posting = self.job_posting_repository.find_by_id(job_posting_id)
        if job_posting is None:
            raise NotFoundError(JOB_POSTING_NOT_FOUND)
        if job_posting.company_id != company_id:
            raise ForbiddenError("La convocatoria no pertenece a esta empresa")
        return job_posting

    def _require_repositories(self):
        if (
            self.job_application_repository is None
            or self.job_posting_repository is None
            or self.profile_repository is None
            or self.practica_repository is None
        ):
            raise RuntimeError("JobApplicationService requires all of its repositories")
