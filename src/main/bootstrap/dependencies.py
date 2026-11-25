from flask import current_app

from application.certificacion_application_service import CertificacionApplicationService
from recruitment.application.job_posting_application_service import JobPostingApplicationService
from profiles.application.company_application_service import CompanyApplicationService
from matching.application.matching_application_service import MatchingApplicationService
from notifications.application.notification_application_service import NotificationApplicationService
from recruitment.application.job_application_service import JobApplicationService
from application.practica_application_service import PracticaApplicationService
from profiles.application.intern_application_service import InternApplicationService
from identity.application.user_application_service import UserApplicationService
from identity.domain.authentication_domain_service import AuthenticationDomainService
from matching.domain.matching_dominio_servicio import MatchingDominioServicio
from identity.infrastructure.smtp_auth_email_sender import SmtpAuthEmailSender
from infrastructure.sqlalchemy_certificado_repository import SqlAlchemyCertificadoRepository
from recruitment.infrastructure.sqlalchemy_job_posting_repository import SqlAlchemyJobPostingRepository
from matching.infrastructure.sqlalchemy_matching_repository import SqlAlchemyMatchingRepository
from notifications.infrastructure.sqlalchemy_notification_repository import SqlAlchemyNotificationRepository
from profiles.infrastructure.sqlalchemy_profile_repository import SqlAlchemyProfileRepository
from recruitment.infrastructure.sqlalchemy_job_application_repository import SqlAlchemyJobApplicationRepository
from infrastructure.sqlalchemy_practica_repository import SqlAlchemyPracticaRepository
from identity.infrastructure.sqlalchemy_user_repository import SqlAlchemyUserRepository
from identity.infrastructure.werkzeug_password_hasher import WerkzeugPasswordHasher


class DependencyContainer:
    """Dependency container and injector for the web layer (SOLID-DIP)."""

    def __init__(self):
        self._repos = {}
        self._services = {}

    # Repository resolvers
    def get_user_repository(self):
        return self._repos.get("user") or SqlAlchemyUserRepository()

    def get_profile_repository(self):
        return self._repos.get("profile") or SqlAlchemyProfileRepository()

    def get_job_posting_repository(self):
        return self._repos.get("job_posting") or SqlAlchemyJobPostingRepository()

    def get_job_application_repository(self):
        return self._repos.get("job_application") or SqlAlchemyJobApplicationRepository()

    def get_practica_repository(self):
        return self._repos.get("practica") or SqlAlchemyPracticaRepository()

    def get_certificado_repository(self):
        return self._repos.get("certificado") or SqlAlchemyCertificadoRepository()

    def get_notification_repository(self):
        return self._repos.get("notification") or SqlAlchemyNotificationRepository()

    def get_matching_repository(self):
        return self._repos.get("matching") or SqlAlchemyMatchingRepository()

    # Application service resolvers
    def get_user_service(self):
        if "user_service" in self._services:
            return self._services["user_service"]
        email_sender = None
        try:
            if current_app:
                email_sender = SmtpAuthEmailSender.from_config(current_app.config)
        except Exception:
            email_sender = SmtpAuthEmailSender()
        return UserApplicationService(
            self.get_user_repository(),
            AuthenticationDomainService(WerkzeugPasswordHasher()),
            email_sender=email_sender,
        )

    def get_job_posting_service(self):
        if "job_posting_service" in self._services:
            return self._services["job_posting_service"]
        return JobPostingApplicationService(self.get_job_posting_repository())

    def get_practica_service(self):
        if "practica_service" in self._services:
            return self._services["practica_service"]
        notif_repo = self.get_notification_repository()
        notif_service = NotificationApplicationService(writer=notif_repo, reader=notif_repo)
        return PracticaApplicationService(
            self.get_practica_repository(),
            self.get_profile_repository(),
            self.get_job_application_repository(),
            self.get_job_posting_repository(),
            notification_service=notif_service,
        )

    def get_job_application_service(self):
        if "job_application_service" in self._services:
            return self._services["job_application_service"]
        notif_repo = self.get_notification_repository()
        notif_service = NotificationApplicationService(writer=notif_repo, reader=notif_repo)
        return JobApplicationService(
            self.get_job_application_repository(),
            self.get_job_posting_repository(),
            self.get_profile_repository(),
            self.get_practica_repository(),
            notification_service=notif_service,
        )

    def get_matching_service(self):
        if "matching_service" in self._services:
            return self._services["matching_service"]
        return MatchingApplicationService(
            self.get_matching_repository(),
            self.get_profile_repository(),
            self.get_job_posting_repository(),
            MatchingDominioServicio(),
        )

    def get_notification_service(self):
        if "notification_service" in self._services:
            return self._services["notification_service"]
        repo = self.get_notification_repository()
        return NotificationApplicationService(writer=repo, reader=repo)

    def get_certificacion_service(self):
        if "certificacion_service" in self._services:
            return self._services["certificacion_service"]
        notif_repo = self.get_notification_repository()
        notif_service = NotificationApplicationService(writer=notif_repo, reader=notif_repo)
        return CertificacionApplicationService(
            self.get_certificado_repository(),
            self.get_practica_repository(),
            self.get_job_application_repository(),
            self.get_job_posting_repository(),
            self.get_profile_repository(),
            notification_service=notif_service,
        )

    def get_intern_service(self):
        if "intern_service" in self._services:
            return self._services["intern_service"]
        return InternApplicationService(
            self.get_profile_repository(),
            self.get_user_repository(),
        )

    def get_company_service(self):
        if "company_service" in self._services:
            return self._services["company_service"]
        return CompanyApplicationService(
            self.get_profile_repository(),
            self.get_user_repository(),
        )

    def override_repository(self, name, repository):
        self._repos[name] = repository

    def override_service(self, name, service):
        self._services[name] = service

    def reset(self):
        self._repos.clear()
        self._services.clear()


container = DependencyContainer()
