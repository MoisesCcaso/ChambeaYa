from typing import Final

from recruitment.api import JobApplication
from internships.domain.internship import Internship
from shared.error_messages import JOB_POSTING_NOT_FOUND, JOB_APPLICATION_NOT_FOUND
from shared.errors import ConflictError, ForbiddenError, NotFoundError

INTERNSHIP_NOT_FOUND: Final = "Práctica no encontrada"


class InternshipApplicationService:
    def __init__(self, internship_repository=None, profiles=None, recruitment=None, notifications=None):
        self.internship_repository = internship_repository
        self.profiles = profiles
        self.recruitment = recruitment
        self.notifications = notifications

    def start_internship(self, company_id, job_application_id):
        self._require_repositories()
        job_application = self.recruitment.find_job_application(job_application_id)
        if job_application is None:
            raise NotFoundError(JOB_APPLICATION_NOT_FOUND)
        if job_application.status != JobApplication.STATUS_SELECTED:
            raise ConflictError("La postulación debe estar seleccionada para iniciar la práctica")

        job_posting = self.recruitment.find_job_posting(job_application.job_posting_id)
        if job_posting is None:
            raise NotFoundError(JOB_POSTING_NOT_FOUND)
        if job_posting.company_id != company_id:
            raise ForbiddenError("La postulación no pertenece a esta empresa")

        existing = self.internship_repository.find_by_job_application_id(job_application_id)
        if existing is not None:
            raise ConflictError("La práctica ya fue iniciada")

        internship = Internship.start(job_application_id, job_application.intern_id)
        return self.internship_repository.save(internship)

    def upload_deliverable(self, user_id, internship_id, file_name):
        self._require_repositories()
        internship = self._get_authorized_internship(user_id, internship_id)
        internship.upload_deliverable(file_name)
        return self.internship_repository.save(internship)

    def get_deliverables_history(self, user_id, internship_id):
        self._require_repositories()
        internship = self._get_visible_internship(user_id, internship_id)
        return internship.get_deliverables_history()

    def delete_deliverable(self, user_id, internship_id, deliverable_id):
        self._require_repositories()
        internship = self._get_authorized_internship(user_id, internship_id)
        removed = internship.remove_deliverable(deliverable_id)
        self.internship_repository.save(internship)
        return removed

    def evaluate(self, company_id, internship_id, score):
        self._require_repositories()
        internship = self.internship_repository.find_by_id(internship_id)
        if internship is None:
            raise NotFoundError(INTERNSHIP_NOT_FOUND)
        job_application = self.recruitment.find_job_application(internship.job_application_id)
        if job_application is None:
            raise NotFoundError(JOB_APPLICATION_NOT_FOUND)

        job_posting = self.recruitment.find_job_posting(job_application.job_posting_id)
        if job_posting is None:
            raise NotFoundError(JOB_POSTING_NOT_FOUND)
        if job_posting.company_id != company_id:
            raise ForbiddenError("La práctica no pertenece a una convocatoria de esta empresa")

        internship.register_evaluation(score)
        saved = self.internship_repository.save(internship)
        self._notify_evaluation(saved)
        return saved

    def _notify_evaluation(self, internship):
        if self.notifications is None or self.profiles is None:
            return
        intern_id = getattr(internship, "intern_id", None)
        if not intern_id:
            return
        try:
            intern = self.profiles.find_intern_by_id(intern_id)
            user_id = getattr(intern, "user_id", None)
            if user_id:
                self.notifications.notify(
                    recipient_user_id=user_id,
                    notification_type="EVALUACION_DISPONIBLE",
                    message="Tu práctica tiene una nueva evaluación disponible",
                    metadata={"practica_id": internship.id},
                )
        except Exception:
            pass

    def get_evaluations_history(self, user_id, internship_id):
        self._require_repositories()
        internship = self._get_visible_internship(user_id, internship_id)
        return internship.get_evaluations_history()

    def delete_evaluation(self, company_id, internship_id, evaluation_id):
        self._require_repositories()
        internship = self.internship_repository.find_by_id(internship_id)
        if internship is None:
            raise NotFoundError(INTERNSHIP_NOT_FOUND)
        self._require_company_owner(company_id, internship)
        deleted = internship.remove_evaluation(evaluation_id)
        self.internship_repository.save(internship)
        return deleted

    def finish(self, company_id, internship_id):
        self._require_repositories()
        internship = self.internship_repository.find_by_id(internship_id)
        if internship is None:
            raise NotFoundError(INTERNSHIP_NOT_FOUND)
        self._require_company_owner(company_id, internship)

        internship.finish()
        return self.internship_repository.save(internship)

    def list_for_user(self, user_id):
        self._require_repositories()
        intern = self.profiles.find_intern_by_user_id(user_id)
        if intern is not None:
            return self.internship_repository.find_by_intern_id(intern.id)

        company = self.profiles.find_company_by_user_id(user_id)
        if company is None:
            raise NotFoundError("Perfil no encontrado")

        return self.internship_repository.find_by_job_application_ids(
            self.recruitment.job_application_ids_for_company(company.id)
        )

    def get_for_user(self, user_id, internship_id):
        self._require_repositories()
        return self._get_visible_internship(user_id, internship_id)

    def _get_authorized_internship(self, user_id, internship_id):
        intern = self.profiles.find_intern_by_user_id(user_id)
        if intern is None:
            raise ForbiddenError("Perfil de practicante no encontrado")

        internship = self.internship_repository.find_by_id(internship_id)
        if internship is None:
            raise NotFoundError(INTERNSHIP_NOT_FOUND)

        if internship.intern_id != intern.id:
            raise ForbiddenError("No autorizado para acceder a esta práctica")

        return internship

    def _get_visible_internship(self, user_id, internship_id):
        internship = self.internship_repository.find_by_id(internship_id)
        if internship is None:
            raise NotFoundError(INTERNSHIP_NOT_FOUND)

        intern = self.profiles.find_intern_by_user_id(user_id)
        if intern is not None and internship.intern_id == intern.id:
            return internship

        company = self.profiles.find_company_by_user_id(user_id)
        if company is not None:
            self._require_company_owner(company.id, internship)
            return internship

        raise ForbiddenError("No autorizado para acceder a esta práctica")

    def _require_company_owner(self, company_id, internship):
        job_application = self.recruitment.find_job_application(internship.job_application_id)
        if job_application is None:
            raise NotFoundError(JOB_APPLICATION_NOT_FOUND)
        job_posting = self.recruitment.find_job_posting(job_application.job_posting_id)
        if job_posting is None:
            raise NotFoundError(JOB_POSTING_NOT_FOUND)
        if job_posting.company_id != company_id:
            raise ForbiddenError("La práctica no pertenece a esta empresa")
        return job_posting

    def _require_repositories(self):
        if any(
            repository is None
            for repository in (
                self.internship_repository,
                self.profiles,
                self.recruitment,
            )
        ):
            raise RuntimeError("InternshipApplicationService requires all of its repositories")
