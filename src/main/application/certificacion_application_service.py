from domain.certificacion.certificacion_dominio_servicio import CertificacionDominioServicio
from shared.error_messages import JOB_POSTING_NOT_FOUND, JOB_APPLICATION_NOT_FOUND
from shared.errors import ForbiddenError, NotFoundError

class CertificacionApplicationService:
    def __init__(self, certificado_repository=None, practica_repository=None,
                 job_application_repository=None, job_posting_repository=None,
                 profile_repository=None, notification_service=None):
        self.certificado_repository = certificado_repository
        self.practica_repository = practica_repository
        self.job_application_repository = job_application_repository
        self.job_posting_repository = job_posting_repository
        self.profile_repository = profile_repository
        self.notification_service = notification_service

    def issue_certificate(self, company_id, practica_id):
        self._require_repositories()

        practica = self.practica_repository.find_by_id(practica_id)
        if practica is None:
            raise NotFoundError("Práctica no encontrada")

        job_application = self.job_application_repository.find_by_id(practica.job_application_id)
        if job_application is None:
            raise NotFoundError(JOB_APPLICATION_NOT_FOUND)

        job_posting = self.job_posting_repository.find_by_id(job_application.job_posting_id)
        if job_posting is None:
            raise NotFoundError(JOB_POSTING_NOT_FOUND)
        if job_posting.company_id != company_id:
            raise ForbiddenError("La práctica no pertenece a una convocatoria de esta empresa")

        intern = self.profile_repository.find_intern_by_id(practica.intern_id)
        if intern is None:
            raise NotFoundError("Practicante no encontrado")

        existing = self.certificado_repository.find_by_practica_id(practica_id)
        if existing is not None:
            return existing, False

        certificado = CertificacionDominioServicio().generar_certificado(
            practica, intern, job_posting
        )
        saved = self.certificado_repository.save(certificado)
        self._notificar_emision(intern, practica_id)
        return saved, True

    def _notificar_emision(self, intern, practica_id):
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
                metadata={"practica_id": practica_id},
            )
        except Exception:
            pass

    def verify_certificate(self, codigo_qr_valor):
        self._require_repositories()

        certificado = self.certificado_repository.find_by_codigo(codigo_qr_valor)
        if certificado is None:
            raise NotFoundError("Certificado no encontrado")

        qr_valido = certificado.verificar_qr(codigo_qr_valor)
        documento_valido = (
            certificado.documento is not None
            and certificado.verificar_integridad(certificado.documento.contenido)
        )
        return qr_valido and documento_valido

    def find_by_practica_id(self, practica_id):
        self._require_repositories()
        return self.certificado_repository.find_by_practica_id(practica_id)

    def _require_repositories(self):
        if any(
            repository is None
            for repository in (
                self.certificado_repository,
                self.practica_repository,
                self.job_application_repository,
                self.job_posting_repository,
                self.profile_repository,
            )
        ):
            raise RuntimeError("CertificacionApplicationService requiere todos sus repositorios")


