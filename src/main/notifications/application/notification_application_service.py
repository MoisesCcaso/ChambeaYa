from notifications.domain.notification import Notification


class NotificationApplicationService:
    def __init__(self, writer=None, reader=None):
        self.writer = writer
        self.reader = reader

    def create_notification(self, recipient_user_id, notification_type, message, metadata=None):
        self._require_writer()
        notification = Notification(
            recipient_user_id=recipient_user_id,
            notification_type=notification_type,
            message=message,
            metadata=metadata,
        )
        return self.writer.save(notification)

    def list_notifications(self, user_id):
        self._require_reader()
        return self.reader.find_by_user_id(user_id)

    def mark_as_read(self, user_id, notification_id):
        self._require_writer()
        return self.writer.mark_as_read(user_id, notification_id)

    def mark_all_as_read(self, user_id):
        self._require_writer()
        return self.writer.mark_all_as_read(user_id)

    def count_unread(self, user_id):
        self._require_reader()
        return self.reader.count_unread(user_id)

    def _require_writer(self):
        if self.writer is None:
            raise RuntimeError("NotificationApplicationService requires a writer")

    def _require_reader(self):
        if self.reader is None:
            raise RuntimeError("NotificationApplicationService requires a reader")
