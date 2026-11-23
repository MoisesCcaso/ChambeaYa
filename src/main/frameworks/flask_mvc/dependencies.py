from flask import current_app

from application.certificacion_application_service import CertificacionApplicationService
from application.convocatoria_application_service import ConvocatoriaApplicationService
from application.empresa_application_service import EmpresaApplicationService
from application.matching_application_service import MatchingApplicationService
from application.notificacion_application_service import NotificacionApplicationService
from application.postulacion_application_service import PostulacionApplicationService
from application.practica_application_service import PracticaApplicationService
from application.practicante_application_service import PracticanteApplicationService
from application.usuario_application_service import UsuarioApplicationService
from domain.auth.autenticacion_dominio_servicio import AutenticacionDominioServicio
from domain.matching.matching_dominio_servicio import MatchingDominioServicio
from infrastructure.smtp_auth_email_sender import SmtpAuthEmailSender
from infrastructure.sqlalchemy_certificado_repository import SqlAlchemyCertificadoRepository
from infrastructure.sqlalchemy_convocatoria_repository import SqlAlchemyConvocatoriaRepository
from infrastructure.sqlalchemy_matching_repository import SqlAlchemyMatchingRepository
from infrastructure.sqlalchemy_notificacion_repository import SqlAlchemyNotificacionRepository
from infrastructure.sqlalchemy_perfil_repository import SqlAlchemyPerfilRepository
from infrastructure.sqlalchemy_postulacion_repository import SqlAlchemyPostulacionRepository
from infrastructure.sqlalchemy_practica_repository import SqlAlchemyPracticaRepository
from infrastructure.sqlalchemy_usuario_repository import SqlAlchemyUsuarioRepository
from infrastructure.werkzeug_password_hasher import WerkzeugPasswordHasher


class DependencyContainer:
    """Contenedor de dependencias e inyector para la capa web (SOLID-DIP)."""

    def __init__(self):
        self._repos = {}
        self._services = {}

    # Resolutores de Repositorios
    def get_usuario_repository(self):
        return self._repos.get("usuario") or SqlAlchemyUsuarioRepository()

    def get_perfil_repository(self):
        return self._repos.get("perfil") or SqlAlchemyPerfilRepository()

    def get_convocatoria_repository(self):
        return self._repos.get("convocatoria") or SqlAlchemyConvocatoriaRepository()

    def get_postulacion_repository(self):
        return self._repos.get("postulacion") or SqlAlchemyPostulacionRepository()

    def get_practica_repository(self):
        return self._repos.get("practica") or SqlAlchemyPracticaRepository()

    def get_certificado_repository(self):
        return self._repos.get("certificado") or SqlAlchemyCertificadoRepository()

    def get_notificacion_repository(self):
        return self._repos.get("notificacion") or SqlAlchemyNotificacionRepository()

    def get_matching_repository(self):
        return self._repos.get("matching") or SqlAlchemyMatchingRepository()

    # Resolutores de Servicios de Aplicación
    def get_usuario_service(self):
        if "usuario_service" in self._services:
            return self._services["usuario_service"]
        email_sender = None
        try:
            if current_app:
                email_sender = SmtpAuthEmailSender.from_config(current_app.config)
        except Exception:
            email_sender = SmtpAuthEmailSender()
        return UsuarioApplicationService(
            self.get_usuario_repository(),
            AutenticacionDominioServicio(WerkzeugPasswordHasher()),
            email_sender=email_sender,
        )

    def get_convocatoria_service(self):
        if "convocatoria_service" in self._services:
            return self._services["convocatoria_service"]
        return ConvocatoriaApplicationService(self.get_convocatoria_repository())

    def get_practica_service(self):
        if "practica_service" in self._services:
            return self._services["practica_service"]
        notif_repo = self.get_notificacion_repository()
        notif_service = NotificacionApplicationService(writer=notif_repo, reader=notif_repo)
        return PracticaApplicationService(
            self.get_practica_repository(),
            self.get_perfil_repository(),
            self.get_postulacion_repository(),
            self.get_convocatoria_repository(),
            notificacion_service=notif_service,
        )

    def get_postulacion_service(self):
        if "postulacion_service" in self._services:
            return self._services["postulacion_service"]
        notif_repo = self.get_notificacion_repository()
        notif_service = NotificacionApplicationService(writer=notif_repo, reader=notif_repo)
        return PostulacionApplicationService(
            self.get_postulacion_repository(),
            self.get_convocatoria_repository(),
            self.get_perfil_repository(),
            self.get_practica_repository(),
            notificacion_service=notif_service,
        )

    def get_matching_service(self):
        if "matching_service" in self._services:
            return self._services["matching_service"]
        return MatchingApplicationService(
            self.get_matching_repository(),
            self.get_perfil_repository(),
            self.get_convocatoria_repository(),
            MatchingDominioServicio(),
        )

    def get_notificacion_service(self):
        if "notificacion_service" in self._services:
            return self._services["notificacion_service"]
        repo = self.get_notificacion_repository()
        return NotificacionApplicationService(writer=repo, reader=repo)

    def get_certificacion_service(self):
        if "certificacion_service" in self._services:
            return self._services["certificacion_service"]
        notif_repo = self.get_notificacion_repository()
        notif_service = NotificacionApplicationService(writer=notif_repo, reader=notif_repo)
        return CertificacionApplicationService(
            self.get_certificado_repository(),
            self.get_practica_repository(),
            self.get_postulacion_repository(),
            self.get_convocatoria_repository(),
            self.get_perfil_repository(),
            notificacion_service=notif_service,
        )

    def get_practicante_service(self):
        if "practicante_service" in self._services:
            return self._services["practicante_service"]
        return PracticanteApplicationService(
            self.get_perfil_repository(),
            self.get_usuario_repository(),
        )

    def get_empresa_service(self):
        if "empresa_service" in self._services:
            return self._services["empresa_service"]
        return EmpresaApplicationService(
            self.get_perfil_repository(),
            self.get_usuario_repository(),
        )

    def override_repository(self, name, repository):
        self._repos[name] = repository

    def override_service(self, name, service):
        self._services[name] = service

    def reset(self):
        self._repos.clear()
        self._services.clear()


container = DependencyContainer()
