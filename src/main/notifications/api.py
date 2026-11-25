"""Public API of the notifications context: the only thing other contexts may use from it."""

__all__ = ["NotificationsApi"]


class NotificationsApi:
    def __init__(self, notification_service):
        self._service = notification_service

    def notify(self, recipient_user_id, notification_type, message, metadata=None):
        return self._service.create_notification(
            recipient_user_id=recipient_user_id,
            notification_type=notification_type,
            message=message,
            metadata=metadata,
        )
