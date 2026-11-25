"""I-19 - Tests for the notifications repository (in-memory SQLite, no doubles).

Code under test: notifications/infrastructure/sqlalchemy_notification_repository.py
"""
import unittest

import pytest
from notifications.domain.notification import Notification
from shared.database import db
from notifications.infrastructure.models.notification_model import NotificationModel
from identity.infrastructure.models.user_model import UserModel
from notifications.infrastructure.sqlalchemy_notification_repository import SqlAlchemyNotificationRepository


class TestNotificationRepository(unittest.TestCase):
    @pytest.fixture(autouse=True)
    def _inject_context(self, app_context):
        self.app_context = app_context

    def setUp(self):
        self.repo = SqlAlchemyNotificationRepository()

    def _create_user(self, email):
        user = UserModel(email=email, password_hash="hash", role="practicante")
        db.session.add(user)
        db.session.commit()
        return user.id

    def _save(self, user_id, message="Hola", notification_type=Notification.TYPE_NEW_SUGGESTIONS,
              metadata=None):
        return self.repo.save(
            Notification(recipient_user_id=user_id, notification_type=notification_type,
                         message=message, metadata=metadata)
        )

    def test_saves_a_new_notification_and_returns_it_with_an_id(self):
        user_id = self._create_user("a@example.com")
        saved = self._save(user_id, "Nueva sugerencia", metadata={"convocatoria_id": 3})

        self.assertIsNotNone(saved.id)
        self.assertEqual(user_id, saved.recipient_user_id)
        self.assertEqual("Nueva sugerencia", saved.message)
        self.assertEqual({"convocatoria_id": 3}, saved.metadata)
        self.assertFalse(saved.is_read)
        self.assertIsNotNone(saved.created_at)

    def test_saving_an_existing_notification_updates_the_record(self):
        user_id = self._create_user("a@example.com")
        saved = self._save(user_id)
        saved.mark_as_read()
        self.repo.save(saved)

        self.assertEqual(1, NotificationModel.query.count())
        self.assertTrue(NotificationModel.query.first().is_read)

    def test_lists_only_the_users_notifications(self):
        u1 = self._create_user("a@example.com")
        u2 = self._create_user("b@example.com")
        own = {self._save(u1, "uno").id, self._save(u1, "dos").id}
        self._save(u2, "ajena")

        result = self.repo.find_by_user_id(u1)

        self.assertEqual(own, {n.id for n in result})

    def test_empty_list_when_the_user_has_no_notifications(self):
        user_id = self._create_user("a@example.com")
        self.assertEqual([], self.repo.find_by_user_id(user_id))

    def test_queries_only_unread_ones(self):
        user_id = self._create_user("a@example.com")
        pending = self._save(user_id, "pendiente")
        read = self._save(user_id, "leida")
        self.repo.mark_as_read(user_id, read.id)

        result = self.repo.find_unread_by_user_id(user_id)

        self.assertEqual([pending.id], [n.id for n in result])

    def test_counts_pending_ones(self):
        user_id = self._create_user("a@example.com")
        other = self._create_user("b@example.com")
        self._save(user_id)
        read = self._save(user_id)
        self._save(other)
        self.repo.mark_as_read(user_id, read.id)

        self.assertEqual(1, self.repo.count_unread(user_id))
        self.assertEqual(1, self.repo.count_unread(other))

    def test_counts_zero_without_notifications(self):
        user_id = self._create_user("a@example.com")
        self.assertEqual(0, self.repo.count_unread(user_id))

    def test_marks_an_own_notification_as_read(self):
        user_id = self._create_user("a@example.com")
        saved = self._save(user_id)

        updated = self.repo.mark_as_read(user_id, saved.id)

        self.assertTrue(updated.is_read)
        self.assertTrue(db.session.get(NotificationModel, saved.id).is_read)

    def test_a_user_cannot_mark_someone_elses_notification_as_read(self):
        owner = self._create_user("a@example.com")
        intruder = self._create_user("b@example.com")
        saved = self._save(owner)

        with self.assertRaises(ValueError):
            self.repo.mark_as_read(intruder, saved.id)

        self.assertFalse(db.session.get(NotificationModel, saved.id).is_read)

    def test_marking_a_missing_notification_raises(self):
        user_id = self._create_user("a@example.com")
        with self.assertRaises(ValueError):
            self.repo.mark_as_read(user_id, 9999)

    def test_mark_all_only_changes_that_users_pending_ones(self):
        u1 = self._create_user("a@example.com")
        u2 = self._create_user("b@example.com")
        self._save(u1)
        self._save(u1)
        foreign = self._save(u2)

        self.repo.mark_all_as_read(u1)

        self.assertEqual(0, self.repo.count_unread(u1))
        self.assertEqual(1, self.repo.count_unread(u2))
        self.assertFalse(db.session.get(NotificationModel, foreign.id).is_read)

    def test_invalid_metadata_is_loaded_as_an_empty_dict(self):
        user_id = self._create_user("a@example.com")
        saved = self._save(user_id)
        db.session.get(NotificationModel, saved.id).metadata_json = "{no es json"
        db.session.commit()

        self.assertEqual({}, self.repo.find_by_user_id(user_id)[0].metadata)


if __name__ == "__main__":
    unittest.main()
