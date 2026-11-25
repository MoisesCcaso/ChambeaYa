from datetime import datetime, timezone


class ExpiringToken:
    def __init__(self, value=None, expires_at=None):
        self.value = value
        self.expires_at = expires_at

    def is_valid(self):
        if not self.value or self.expires_at is None:
            return False

        expires_at = self.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)

        return expires_at > datetime.now(timezone.utc)
