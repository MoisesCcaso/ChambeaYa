import re

from identity.application.email_delivery_error import EmailDeliveryError
from identity.domain.user import User
from shared.errors import AuthenticationError, ConflictError, DomainError


EMAIL_PATTERN = re.compile(
    r"^[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@"
    r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?"
    r"(?:\.[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?)+$"
)


class UserApplicationService:
    def __init__(
        self,
        user_repository=None,
        authentication_domain_service=None,
        email_sender=None,
    ):
        self.user_repository = user_repository
        self.authentication_domain_service = authentication_domain_service
        self.email_sender = email_sender

    def register_user(self, email, password, password_confirmation, role):
        self._require_repository()
        self._require_email_sender()

        normalized_email = self._normalize_email(email)
        if self.user_repository.find_by_email(normalized_email) is not None:
            raise ConflictError(
                "El correo ya está registrado. Si la cuenta está pendiente, "
                "solicita un nuevo enlace de activación."
            )
        if password != password_confirmation:
            raise DomainError("Las contraseñas no coinciden")

        password_hash = self.authentication_domain_service.generate_password_hash(password)
        user = User(
            email=normalized_email,
            password_hash=password_hash,
            role=role,
            status=User.STATUS_PENDING,
        )
        user.register()
        user.assign_activation_token(
            self.authentication_domain_service.generate_token(valid_hours=48)
        )

        user = self.user_repository.save(user)
        try:
            self.email_sender.send_activation(
                user.email,
                user.activation_token,
            )
        except EmailDeliveryError as exc:
            raise EmailDeliveryError(
                "La cuenta fue creada, pero el correo no pudo enviarse. "
                "Solicita un nuevo enlace de activación."
            ) from exc
        return user

    def authenticate(self, email, password):
        self._require_repository()

        user = self.user_repository.find_by_email(self._normalize_email(email))
        if not self.authentication_domain_service.authenticate(user, password):
            raise AuthenticationError("Credenciales inválidas")

        return user

    def recover_password(self, email):
        self._require_repository()
        self._require_email_sender()

        user = self.user_repository.find_by_email(self._normalize_email(email))
        if user is None:
            return None

        user.assign_password_reset_token(
            self.authentication_domain_service.generate_token(valid_hours=2)
        )
        user = self.user_repository.save(user)
        self.email_sender.send_password_reset(
            user.email,
            user.password_reset_token,
        )
        return user

    def resend_activation(self, email):
        self._require_repository()
        self._require_email_sender()

        user = self.user_repository.find_by_email(self._normalize_email(email))
        if user is None or user.status == User.STATUS_ACTIVE:
            return None

        user.assign_activation_token(
            self.authentication_domain_service.generate_token(valid_hours=48)
        )
        user = self.user_repository.save(user)
        self.email_sender.send_activation(
            user.email,
            user.activation_token,
        )
        return user

    def activate_account(self, token):
        self._require_repository()

        if not token:
            raise DomainError("El token de activación es obligatorio")

        user = self.user_repository.find_by_activation_token(token)
        if user is None:
            raise DomainError("Token de activación inválido")

        if not self.authentication_domain_service.validate_token(
            user.activation,
        ):
            raise DomainError("Token de activación expirado")

        user.activate()
        return self.user_repository.save(user)

    def reset_password(self, token, new_password):
        self._require_repository()

        if not token:
            raise DomainError("El token de recuperación es obligatorio")

        user = self.user_repository.find_by_password_reset_token(token)
        if user is None:
            raise DomainError("Token de recuperación inválido")

        if not self.authentication_domain_service.validate_token(
            user.password_reset,
        ):
            raise DomainError("Token de recuperación expirado")

        password_hash = self.authentication_domain_service.generate_password_hash(new_password)
        user.update_password(password_hash)
        return self.user_repository.save(user)

    def find_by_id(self, user_id):
        self._require_repository()
        return self.user_repository.find_by_id(user_id)

    def _require_repository(self):
        if self.user_repository is None:
            raise RuntimeError("UserApplicationService requires a repository")

    def _require_email_sender(self):
        if self.email_sender is None:
            raise RuntimeError("UserApplicationService requires an email sender")

    def _normalize_email(self, email):
        if not email:
            raise DomainError("El email es obligatorio")

        normalized = str(email).strip().lower()
        if len(normalized) > 254 or not EMAIL_PATTERN.fullmatch(normalized):
            raise DomainError("El email no es válido")
        return normalized
