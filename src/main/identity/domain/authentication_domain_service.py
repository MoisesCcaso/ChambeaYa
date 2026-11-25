from datetime import datetime, timedelta, timezone
from secrets import token_urlsafe

from identity.domain.expiring_token import ExpiringToken
from shared.errors import DomainError


class AuthenticationDomainService:
    def __init__(self, password_hasher):
        self.password_hasher = password_hasher    
    
    def generate_password_hash(self, password):
        if not password:
            raise DomainError("La contraseña es obligatoria")
        password = str(password)
        if len(password) < 8:
            raise DomainError("La contraseña debe tener al menos 8 caracteres")
        if len(password) > 128:
            raise DomainError("La contraseña no puede superar 128 caracteres")
        if not any(character.islower() for character in password):
            raise DomainError("La contraseña debe incluir una letra minúscula")
        if not any(character.isupper() for character in password):
            raise DomainError("La contraseña debe incluir una letra mayúscula")
        if not any(character.isdigit() for character in password):
            raise DomainError("La contraseña debe incluir un número")

        return self.password_hasher.hash(password)

    def authenticate(self, user, password):
        if user is None:
            return False

        user.login()
        return self.password_hasher.verify(user.password_hash, password)

    def generate_token(self, valid_hours=24):
        expires_at = datetime.now(timezone.utc) + timedelta(hours=valid_hours)
        return ExpiringToken(token_urlsafe(32), expires_at)

    def validate_token(self, value, expires_at=None):
        if isinstance(value, ExpiringToken):
            return value.is_valid()
        return ExpiringToken(value, expires_at).is_valid()
