import json

from notifications.domain.notification import Notification
from notifications.domain.i_notification_writer import INotificationWriter
from notifications.domain.i_notification_reader import INotificationReader
from shared.database import db
from notifications.infrastructure.models.notification_model import NotificationModel
from shared.errors import NotFoundError


class SqlAlchemyNotificationRepository(INotificationWriter, INotificationReader):
    def save(self, notification):
        model = None
        if notification.id is not None:
            model = db.session.get(NotificationModel, notification.id)

        if model is None:
            model = NotificationModel(
                recipient_user_id=notification.recipient_user_id,
                notification_type=notification.notification_type,
                message=notification.message,
            )
            db.session.add(model)

        model.is_read = notification.is_read
        model.metadata_json = self._dump_json(notification.metadata)

        db.session.commit()
        return self._to_domain(model)

    def mark_as_read(self, user_id, notification_id):
        model = NotificationModel.query.filter_by(
            id=notification_id,
            recipient_user_id=user_id,
        ).first()
        if model is None:
            raise NotFoundError("Notificación no encontrada")
        model.is_read = True
        db.session.commit()
        return self._to_domain(model)

    def mark_all_as_read(self, user_id):
        NotificationModel.query.filter_by(
            recipient_user_id=user_id, is_read=False
        ).update({NotificationModel.is_read: True})
        db.session.commit()

    def find_by_user_id(self, user_id):
        models = (
            NotificationModel.query
            .filter_by(recipient_user_id=user_id)
            .order_by(NotificationModel.created_at.desc())
            .all()
        )
        return [self._to_domain(m) for m in models]

    def find_unread_by_user_id(self, user_id):
        models = (
            NotificationModel.query
            .filter_by(recipient_user_id=user_id, is_read=False)
            .order_by(NotificationModel.created_at.desc())
            .all()
        )
        return [self._to_domain(m) for m in models]

    def count_unread(self, user_id):
        return NotificationModel.query.filter_by(
            recipient_user_id=user_id, is_read=False
        ).count()

    def _to_domain(self, model):
        if model is None:
            return None
        return Notification(
            id=model.id,
            recipient_user_id=model.recipient_user_id,
            notification_type=model.notification_type,
            message=model.message,
            metadata=self._load_json(model.metadata_json),
            is_read=model.is_read,
            created_at=model.created_at,
        )

    def _dump_json(self, value):
        if not value:
            return "{}"
        return json.dumps(value, ensure_ascii=False)

    def _load_json(self, value):
        if not value:
            return {}
        try:
            parsed = json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return {}
        if not isinstance(parsed, dict):
            return {}
        return parsed
