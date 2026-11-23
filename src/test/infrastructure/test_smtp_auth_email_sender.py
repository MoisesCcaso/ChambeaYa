import ssl
import unittest
from unittest.mock import MagicMock, patch

from infrastructure.smtp_auth_email_sender import SmtpAuthEmailSender


class TestSmtpAuthEmailSender(unittest.TestCase):
    def setUp(self):
        self.sender = SmtpAuthEmailSender(
            delivery_mode="smtp",
            server="smtp.example.com",
            port=587,
            username="user",
            password="password",
            use_tls=True,
            use_ssl=False,
        )

    def test_create_ssl_context_enforces_hostname_and_cert_validation(self):
        context = self.sender._create_ssl_context()
        self.assertTrue(context.check_hostname)
        self.assertEqual(context.verify_mode, ssl.CERT_REQUIRED)

    @patch("smtplib.SMTP")
    def test_send_uses_explicit_tls_context(self, mock_smtp_cls):
        mock_smtp = MagicMock()
        mock_smtp_cls.return_value.__enter__.return_value = mock_smtp

        self.sender.send_activation("test@example.com", "token123")

        mock_smtp.starttls.assert_called_once()
        _, kwargs = mock_smtp.starttls.call_args
        context = kwargs.get("context")
        self.assertIsNotNone(context)
        self.assertTrue(context.check_hostname)
        self.assertEqual(context.verify_mode, ssl.CERT_REQUIRED)

    @patch("smtplib.SMTP_SSL")
    def test_send_uses_explicit_ssl_context(self, mock_ssl_cls):
        mock_smtp = MagicMock()
        mock_ssl_cls.return_value.__enter__.return_value = mock_smtp
        ssl_sender = SmtpAuthEmailSender(
            delivery_mode="smtp",
            server="smtp.example.com",
            port=465,
            username="user",
            password="password",
            use_tls=False,
            use_ssl=True,
        )

        ssl_sender.send_activation("test@example.com", "token123")

        mock_ssl_cls.assert_called_once()
        _, kwargs = mock_ssl_cls.call_args
        context = kwargs.get("context")
        self.assertIsNotNone(context)
        self.assertTrue(context.check_hostname)
        self.assertEqual(context.verify_mode, ssl.CERT_REQUIRED)
