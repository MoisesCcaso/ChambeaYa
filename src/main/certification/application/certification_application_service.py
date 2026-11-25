from certification.domain.certification_domain_service import CertificationDomainService
from shared.error_messages import JOB_POSTING_NOT_FOUND, JOB_APPLICATION_NOT_FOUND
from shared.errors import ForbiddenError, NotFoundError

class CertificationApplicationService:
    def __init__(self, certificate_repository=None, internships=None,
                 recruitment=None, profiles=None, notifications=None):
        self.certificate_repository = certificate_repository
        self.internships = internships
        self.recruitment = recruitment
        self.profiles = profiles
        self.notifications = notifications

    def issue_certificate(self, company_id, internship_id):
        self._require_repositories()

        internship = self.internships.find_internship(internship_id)
        if internship is None:
            raise NotFoundError("Práctica no encontrada")

        job_application = self.recruitment.find_job_application(internship.job_application_id)
        if job_application is None:
            raise NotFoundError(JOB_APPLICATION_NOT_FOUND)

        job_posting = self.recruitment.find_job_posting(job_application.job_posting_id)
        if job_posting is None:
            raise NotFoundError(JOB_POSTING_NOT_FOUND)
        if job_posting.company_id != company_id:
            raise ForbiddenError("La práctica no pertenece a una convocatoria de esta empresa")

        intern = self.profiles.find_intern_by_id(internship.intern_id)
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
        if self.notifications is None:
            return
        user_id = getattr(intern, "user_id", None)
        if not user_id:
            return
        try:
            self.notifications.notify(
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
                self.internships,
                self.recruitment,
                self.profiles,
            )
        ):
            raise RuntimeError("CertificationApplicationService requires all of its repositories")


