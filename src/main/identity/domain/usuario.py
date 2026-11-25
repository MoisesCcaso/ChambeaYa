from identity.domain.token_recuperacion import TokenRecuperacion
from shared.errors import DomainError, ForbiddenError


class Usuario:
    ESTADO_ACTIVO = "activo"
    ESTADO_PENDIENTE = "pendiente"
    TIPO_EMPRESA = "empresa"
    TIPO_PRACTICANTE = "practicante"

    def __init__(
        self,
        id=None,
        email=None,
        password_hash=None,
        tipo=None,
        estado=None,
        activation_token=None,
        activation_token_expires_at=None,
        password_reset_token=None,
        password_reset_expires_at=None,
        token_activacion=None,
        token_recuperacion=None,
    ):
        self.id = id
        self.email = email
        self.password_hash = password_hash
        self.tipo = tipo
        self.estado = estado or self.ESTADO_PENDIENTE

        if token_activacion is not None:
            self._token_activacion = token_activacion
        elif activation_token is not None or activation_token_expires_at is not None:
            self._token_activacion = TokenRecuperacion(activation_token, activation_token_expires_at)
        else:
            self._token_activacion = None

        if token_recuperacion is not None:
            self._token_recuperacion = token_recuperacion
        elif password_reset_token is not None or password_reset_expires_at is not None:
            self._token_recuperacion = TokenRecuperacion(password_reset_token, password_reset_expires_at)
        else:
            self._token_recuperacion = None

    @property
    def token_activacion(self):
        return self._token_activacion

    @token_activacion.setter
    def token_activacion(self, token):
        self._token_activacion = token

    @property
    def token_recuperacion(self):
        return self._token_recuperacion

    @token_recuperacion.setter
    def token_recuperacion(self, token):
        self._token_recuperacion = token

    @property
    def activation_token(self):
        return self._token_activacion.valor if self._token_activacion else None

    @activation_token.setter
    def activation_token(self, valor):
        if self._token_activacion:
            self._token_activacion.valor = valor
        elif valor is not None:
            self._token_activacion = TokenRecuperacion(valor=valor)

    @property
    def activation_token_expires_at(self):
        return self._token_activacion.expiracion if self._token_activacion else None

    @activation_token_expires_at.setter
    def activation_token_expires_at(self, expiracion):
        if self._token_activacion:
            self._token_activacion.expiracion = expiracion
        elif expiracion is not None:
            self._token_activacion = TokenRecuperacion(expiracion=expiracion)

    @property
    def password_reset_token(self):
        return self._token_recuperacion.valor if self._token_recuperacion else None

    @password_reset_token.setter
    def password_reset_token(self, valor):
        if self._token_recuperacion:
            self._token_recuperacion.valor = valor
        elif valor is not None:
            self._token_recuperacion = TokenRecuperacion(valor=valor)

    @property
    def password_reset_expires_at(self):
        return self._token_recuperacion.expiracion if self._token_recuperacion else None

    @password_reset_expires_at.setter
    def password_reset_expires_at(self, expiracion):
        if self._token_recuperacion:
            self._token_recuperacion.expiracion = expiracion
        elif expiracion is not None:
            self._token_recuperacion = TokenRecuperacion(expiracion=expiracion)

    def registrar(self):
        if not self.email:
            raise DomainError("El email es obligatorio")
        if not self.password_hash:
            raise DomainError("La contraseña es obligatoria")
        if self.tipo not in {self.TIPO_PRACTICANTE, self.TIPO_EMPRESA}:
            raise DomainError("El tipo de usuario no es válido")

        return self

    def login(self):
        if self.estado != self.ESTADO_ACTIVO:
            raise ForbiddenError("La cuenta no está activa")

        return self

    def activar(self):
        self.estado = self.ESTADO_ACTIVO
        self._token_activacion = None
        return self

    def asignar_token_activacion(self, token):
        self._token_activacion = token
        return self

    def asignar_token_recuperacion(self, token):
        self._token_recuperacion = token
        return self

    def token_activacion_vigente(self):
        return self._token_activacion.esta_vigente() if self._token_activacion else False

    def token_recuperacion_vigente(self):
        return self._token_recuperacion.esta_vigente() if self._token_recuperacion else False

    def actualizar_password(self, password_hash):
        if not password_hash:
            raise DomainError("La contraseña es obligatoria")

        self.password_hash = password_hash
        self._token_recuperacion = None
        return self
