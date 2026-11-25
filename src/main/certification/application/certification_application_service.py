from certification.domain.certification_domain_service import CertificationDomainService
from shared.error_messages import JOB_POSTING_NOT_FOUND, JOB_APPLICATION_NOT_FOUND
from shared.errors import ForbiddenError, NotFoundError

class CertificationApplicationService:
    def __init__(self, certificate_repository=None, internship_repository=None,
                 job_application_repository=None, job_posting_repository=None,
                 profile_repository=None, notification_service=None):
        self.certificate_repository = certificate_repository
        self.internship_repository = internship_repository
        self.job_application_repository = job_application_repository
        self.job_posting_repository = job_posting_repository
        self.profile_repository = profile_repository
        self.notification_service = notification_service

    def issue_certificate(self, company_id, internship_id):
        self._require_repositories()

        internship = self.internship_repository.find_by_id(internship_id)
        if internship is None:
            raise NotFoundError("Práctica no encontrada")

        job_application = self.job_application_repository.find_by_id(internship.job_application_id)
        if job_application is None:
            raise NotFoundError(JOB_APPLICATION_NOT_FOUND)

        job_posting = self.job_posting_repository.find_by_id(job_application.job_posting_id)
        if job_posting is None:
            raise NotFoundError(JOB_POSTING_NOT_FOUND)
        if job_posting.company_id != company_id:
            raise ForbiddenError("La práctica no pertenece a una convocatoria de esta empresa")

        intern = self.profile_repository.find_intern_by_id(internship.intern_id)
        if intern is None:
            raise NotFoundError("Practicante no encontrado")

        existing = self.certificate_repository.find_by_internship_id(internship_id)
        if existing is not None:
            return existing, False

        certificate = CertificationDomainService().generate_certificate(
            internship, intern, job_posting
        )
        saved = self.certificate_repository.save(certificate)
        self._notify_issuance(intern, internship_id)
        return saved, True

    def _notify_issuance(self, intern, internship_id):
        if self.notification_service is None:
            return
        user_id = getattr(intern, "user_id", None)
        if not user_id:
            return
        try:
            self.notification_service.create_notification(
                recipient_user_id=user_id,
                notification_type="CERTIFICADO_EMITIDO",
                message="Tu certificado digital ha sido emitido",
                metadata={"practica_id": internship_id},
            )
        except Exception:
            pass

    def verify_certificate(self, qr_code_value):
        self._require_repositories()

        certificate = self.certificate_repository.find_by_code(qr_code_value)
        if certificate is None:
            raise NotFoundError("Certificado no encontrado")

        qr_valid = certificate.verify_qr(qr_code_value)
        document_valid = (
            certificate.document is not None
            and certificate.verify_integrity(certificate.document.content)
        )
        return qr_valid and document_valid

    def find_by_internship_id(self, internship_id):
        self._require_repositories()
        return self.certificate_repository.find_by_internship_id(internship_id)

    def _require_repositories(self):
        if any(
            repository is None
            for repository in (
                self.certificate_repository,
                self.internship_repository,
                self.job_application_repository,
                self.job_posting_repository,
                self.profile_repository,
            )
        ):
            raise RuntimeError("CertificationApplicationService requires all of its repositories")


