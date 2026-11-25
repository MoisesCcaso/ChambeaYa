from flask import current_app

from identity.api import IdentityApi
from internships.api import InternshipsApi
from notifications.api import NotificationsApi
from profiles.api import ProfilesApi
from recruitment.api import RecruitmentApi

from certification.application.certification_application_service import CertificationApplicationService
from recruitment.application.job_posting_application_service import JobPostingApplicationService
from profiles.application.company_application_service import CompanyApplicationService
from matching.application.matching_application_service import MatchingApplicationService
from notifications.application.notification_application_service import NotificationApplicationService
from recruitment.application.job_application_service import JobApplicationService
from internships.application.internship_application_service import InternshipApplicationService
from profiles.application.intern_application_service import InternApplicationService
from identity.application.user_application_service import UserApplicationService
from identity.domain.authentication_domain_service import AuthenticationDomainService
from matching.domain.matching_domain_service import MatchingDomainService
from identity.infrastructure.smtp_auth_email_sender import SmtpAuthEmailSender
from certification.infrastructure.sqlalchemy_certificate_repository import SqlAlchemyCertificateRepository
from recruitment.infrastructure.sqlalchemy_job_posting_repository import SqlAlchemyJobPostingRepository
from matching.infrastructure.sqlalchemy_matching_repository import SqlAlchemyMatchingRepository
from notifications.infrastructure.sqlalchemy_notification_repository import SqlAlchemyNotificationRepository
from profiles.infrastructure.sqlalchemy_profile_repository import SqlAlchemyProfileRepository
from recruitment.infrastructure.sqlalchemy_job_application_repository import SqlAlchemyJobApplicationRepository
from internships.infrastructure.sqlalchemy_internship_repository import SqlAlchemyInternshipRepository
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

    def get_internship_repository(self):
        return self._repos.get("internship") or SqlAlchemyInternshipRepository()

    def get_certificate_repository(self):
        return self._repos.get("certificate") or SqlAlchemyCertificateRepository()

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

    def get_internship_service(self):
        if "internship_service" in self._services:
            return self._services["internship_service"]
        return InternshipApplicationService(
            self.get_internship_repository(),
            profiles=self.get_profiles_api(),
            recruitment=self.get_recruitment_api(),
            notifications=self.get_notifications_api(),
        )

    def get_job_application_service(self):
        if "job_application_service" in self._services:
            return self._services["job_application_service"]
        return JobApplicationService(
            self.get_job_application_repository(),
            self.get_job_posting_repository(),
            profiles=self.get_profiles_api(),
            internships=self.get_internships_api(),
            notifications=self.get_notifications_api(),
        )

    def get_matching_service(self):
        if "matching_service" in self._services:
            return self._services["matching_service"]
        return MatchingApplicationService(
            self.get_matching_repository(),
            profiles=self.get_profiles_api(),
            recruitment=self.get_recruitment_api(),
            matching_domain_service=MatchingDomainService(),
        )

    def get_notification_service(self):
        if "notification_service" in self._services:
            return self._services["notification_service"]
        repo = self.get_notification_repository()
        return NotificationApplicationService(writer=repo, reader=repo)

    def get_certification_service(self):
        if "certification_service" in self._services:
            return self._services["certification_service"]
        return CertificationApplicationService(
            self.get_certificate_repository(),
            internships=self.get_internships_api(),
            recruitment=self.get_recruitment_api(),
            profiles=self.get_profiles_api(),
            notifications=self.get_notifications_api(),
        )

    def get_intern_service(self):
        if "intern_service" in self._services:
            return self._services["intern_service"]
        return InternApplicationService(self.get_profile_repository(), identity=self.get_identity_api())

    def get_company_service(self):
        if "company_service" in self._services:
            return self._services["company_service"]
        return CompanyApplicationService(self.get_profile_repository(), identity=self.get_identity_api())

    # Public APIs: the only way a context reaches another one
    def get_identity_api(self):
        return IdentityApi(self.get_user_repository())

    def get_profiles_api(self):
        return ProfilesApi(self.get_profile_repository())

    def get_recruitment_api(self):
        return RecruitmentApi(self.get_job_posting_repository(), self.get_job_application_repository())

    def get_internships_api(self):
        return InternshipsApi(self.get_internship_repository(), self.get_internship_service())

    def get_notifications_api(self):
        return NotificationsApi(self.get_notification_service())

    def override_repository(self, name, repository):
        self._repos[name] = repository

    def override_service(self, name, service):
        self._services[name] = service

    def reset(self):
        self._repos.clear()
        self._services.clear()


container = DependencyContainer()
