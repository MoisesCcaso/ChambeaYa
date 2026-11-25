"""I-22 - Tests for the notifications application service (autospec doubles).

Code under test: notifications/application/notification_application_service.py
"""
import unittest
from unittest.mock import create_autospec

from notifications.application.notification_application_service import NotificationApplicationService
from notifications.domain.i_notification_reader import INotificationReader
from notifications.domain.i_notification_writer import INotificationWriter
from notifications.domain.notification import Notification


class TestNotificationService(unittest.TestCase):
    def setUp(self):
        self.reader = create_autospec(INotificationReader, instance=True)
        self.writer = create_autospec(INotificationWriter, instance=True)
        self.service = NotificationApplicationService(writer=self.writer, reader=self.reader)

    def test_lists_notifications_delegating_to_the_reader(self):
        expected = [Notification(id=1), Notification(id=2)]
        self.reader.find_by_user_id.return_value = expected

        result = self.service.list_notifications(5)

        self.assertEqual(expected, result)
        self.reader.find_by_user_id.assert_called_once_with(5)

    def test_marks_a_notification_as_read_with_the_right_user_and_id(self):
        read = Notification(id=9, is_read=True)
        self.writer.mark_as_read.return_value = read

        result = self.service.mark_as_read(5, 9)

        self.assertIs(read, result)
        self.writer.mark_as_read.assert_called_once_with(5, 9)

    def test_marking_someone_elses_notification_propagates_the_writer_error(self):
        self.writer.mark_as_read.side_effect = ValueError("Notificación no encontrada")
        with self.assertRaises(ValueError):
            self.service.mark_as_read(5, 9)

    def test_marks_all_as_read_for_the_user(self):
        self.service.mark_all_as_read(5)
        self.writer.mark_all_as_read.assert_called_once_with(5)

    def test_counts_unread_delegating_to_the_reader(self):
        self.reader.count_unread.return_value = 3

        self.assertEqual(3, self.service.count_unread(5))
        self.reader.count_unread.assert_called_once_with(5)

    def test_creates_a_notification_and_saves_it_with_the_writer(self):
        self.writer.save.side_effect = lambda notification: notification

        created = self.service.create_notification(
            5, Notification.TYPE_CERTIFICATE_ISSUED, "Tu certificado está listo",
            metadata={"practica_id": 7},
        )

        self.writer.save.assert_called_once_with(created)
        self.assertEqual(5, created.recipient_user_id)
        self.assertEqual(Notification.TYPE_CERTIFICATE_ISSUED, created.notification_type)
        self.assertEqual("Tu certificado está listo", created.message)
        self.assertEqual({"practica_id": 7}, created.metadata)
        self.assertFalse(created.is_read)

    def test_creating_a_notification_without_metadata_uses_an_empty_dict(self):
        self.writer.save.side_effect = lambda notification: notification
        created = self.service.create_notification(5, Notification.TYPE_NEW_SUGGESTIONS, "Hola")
        self.assertEqual({}, created.metadata)

    def test_the_reader_is_not_used_for_write_operations(self):
        self.service.mark_all_as_read(5)
        self.service.mark_as_read(5, 1)
        self.assertEqual([], self.reader.method_calls)

    def test_the_writer_is_not_used_for_read_operations(self):
        self.service.list_notifications(5)
        self.service.count_unread(5)
        self.assertEqual([], self.writer.method_calls)

    def test_without_a_writer_writes_raise_runtime_error(self):
        service = NotificationApplicationService(reader=self.reader)
        with self.assertRaises(RuntimeError):
            service.create_notification(5, "T", "m")
        with self.assertRaises(RuntimeError):
            service.mark_as_read(5, 1)
        with self.assertRaises(RuntimeError):
            service.mark_all_as_read(5)

    def test_without_a_reader_reads_raise_runtime_error(self):
        service = NotificationApplicationService(writer=self.writer)
        with self.assertRaises(RuntimeError):
            service.list_notifications(5)
        with self.assertRaises(RuntimeError):
            service.count_unread(5)


if __name__ == "__main__":
    unittest.main()
