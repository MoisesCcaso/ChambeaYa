from identity.domain.expiring_token import ExpiringToken
from shared.errors import DomainError, ForbiddenError


class User:
    STATUS_ACTIVE = "activo"
    STATUS_PENDING = "pendiente"
    ROLE_COMPANY = "empresa"
    ROLE_INTERN = "practicante"

    def __init__(
        self,
        id=None,
        email=None,
        password_hash=None,
        role=None,
        status=None,
        activation_token=None,
        activation_token_expires_at=None,
        password_reset_token=None,
        password_reset_expires_at=None,
        activation=None,
        password_reset=None,
    ):
        self.id = id
        self.email = email
        self.password_hash = password_hash
        self.role = role
        self.status = status or self.STATUS_PENDING

        if activation is not None:
            self._activation = activation
        elif activation_token is not None or activation_token_expires_at is not None:
            self._activation = ExpiringToken(activation_token, activation_token_expires_at)
        else:
            self._activation = None

        if password_reset is not None:
            self._password_reset = password_reset
        elif password_reset_token is not None or password_reset_expires_at is not None:
            self._password_reset = ExpiringToken(password_reset_token, password_reset_expires_at)
        else:
            self._password_reset = None

    @property
    def activation(self):
        return self._activation

    @activation.setter
    def activation(self, token):
        self._activation = token

    @property
    def password_reset(self):
        return self._password_reset

    @password_reset.setter
    def password_reset(self, token):
        self._password_reset = token

    @property
    def activation_token(self):
        return self._activation.value if self._activation else None

    @activation_token.setter
    def activation_token(self, value):
        if self._activation:
            self._activation.value = value
        elif value is not None:
            self._activation = ExpiringToken(value=value)

    @property
    def activation_token_expires_at(self):
        return self._activation.expires_at if self._activation else None

    @activation_token_expires_at.setter
    def activation_token_expires_at(self, expires_at):
        if self._activation:
            self._activation.expires_at = expires_at
        elif expires_at is not None:
            self._activation = ExpiringToken(expires_at=expires_at)

    @property
    def password_reset_token(self):
        return self._password_reset.value if self._password_reset else None

    @password_reset_token.setter
    def password_reset_token(self, value):
        if self._password_reset:
            self._password_reset.value = value
        elif value is not None:
            self._password_reset = ExpiringToken(value=value)

    @property
    def password_reset_expires_at(self):
        return self._password_reset.expires_at if self._password_reset else None

    @password_reset_expires_at.setter
    def password_reset_expires_at(self, expires_at):
        if self._password_reset:
            self._password_reset.expires_at = expires_at
        elif expires_at is not None:
            self._password_reset = ExpiringToken(expires_at=expires_at)

    def register(self):
        if not self.email:
            raise DomainError("El email es obligatorio")
        if not self.password_hash:
            raise DomainError("La contraseña es obligatoria")
        if self.role not in {self.ROLE_INTERN, self.ROLE_COMPANY}:
            raise DomainError("El tipo de usuario no es válido")

        return self

    def login(self):
        if self.status != self.STATUS_ACTIVE:
            raise ForbiddenError("La cuenta no está activa")

        return self

    def activate(self):
        self.status = self.STATUS_ACTIVE
        self._activation = None
        return self

    def assign_activation_token(self, token):
        self._activation = token
        return self

    def assign_password_reset_token(self, token):
        self._password_reset = token
        return self

    def has_valid_activation_token(self):
        return self._activation.is_valid() if self._activation else False

    def has_valid_password_reset_token(self):
        return self._password_reset.is_valid() if self._password_reset else False

    def update_password(self, password_hash):
        if not password_hash:
            raise DomainError("La contraseña es obligatoria")

        self.password_hash = password_hash
        self._password_reset = None
        return self
