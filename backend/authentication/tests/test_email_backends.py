import json
from io import StringIO
from unittest.mock import patch
from urllib.error import HTTPError, URLError

from django.core import mail
from django.core.management import call_command
from django.test import SimpleTestCase, override_settings

from authentication.email_backends import BrevoEmailBackend, EmailDeliveryError, NoRedirect


class BrevoDeliveryTests(SimpleTestCase):
    def setUp(self):
        self.backend = BrevoEmailBackend(api_key="synthetic-private-api-key")
        self.message = mail.EmailMessage(
            "Reset your IDSC Clinic password", "https://clinic.example.test/#reset-password?token=synthetic",
            "IDSC Clinic <sender@example.test>", ["recipient@example.test"],
        )

    def test_https_delivery_preserves_sender_recipient_and_reset_link(self):
        with patch("authentication.email_backends.build_opener") as opener:
            response = opener.return_value.open.return_value.__enter__.return_value
            response.status = 201
            response.read.return_value = b'{"messageId":"synthetic-message"}'
            self.assertEqual(self.backend.send_messages([self.message]), 1)
            request = opener.return_value.open.call_args.args[0]
            self.assertEqual(request.full_url, "https://api.brevo.com/v3/smtp/email")
            self.assertEqual(request.method, "POST")
            self.assertEqual(request.get_header("Api-key"), "synthetic-private-api-key")
            data = json.loads(request.data)
            self.assertEqual(data["to"], [{"email": "recipient@example.test"}])
            self.assertEqual(data["sender"], {"email": "sender@example.test", "name": "IDSC Clinic"})
            self.assertEqual(data["textContent"], self.message.body)

    def test_failure_does_not_leak_provider_body_token_or_api_key(self):
        for error in [URLError("private-token-and-key"), HTTPError("https://api.brevo.com", 429, "private-token-and-key", {}, None)]:
            with self.subTest(error=type(error).__name__), patch("authentication.email_backends.build_opener") as opener:
                opener.return_value.open.side_effect = error
                with self.assertRaises(EmailDeliveryError) as result:
                    self.backend.send_messages([self.message])
                self.assertEqual(str(result.exception), "Email provider request failed.")
                self.assertEqual(opener.return_value.open.call_count, 1)

    def test_provider_must_accept_message_and_return_identifier(self):
        for status, body in [(200, b'{"messageId":"x"}'), (201, b'{}'), (201, b'not-json')]:
            with self.subTest(status=status, body=body), patch("authentication.email_backends.build_opener") as opener:
                response = opener.return_value.open.return_value.__enter__.return_value
                response.status, response.read.return_value = status, body
                with self.assertRaises(EmailDeliveryError):
                    self.backend.send_messages([self.message])

    def test_redirects_never_forward_credentials_or_messages(self):
        self.assertIsNone(NoRedirect().redirect_request(None, None, 302, "Found", {}, "https://other.invalid"))

    def test_missing_key_or_invalid_sender_never_contacts_provider(self):
        with patch("authentication.email_backends.build_opener") as opener:
            with self.assertRaises(EmailDeliveryError):
                BrevoEmailBackend().send_messages([self.message])
            self.message.from_email = "not-an-email"
            with self.assertRaises(EmailDeliveryError):
                self.backend.send_messages([self.message])
            opener.assert_not_called()

    def test_empty_messages_and_unsupported_recipient_copies(self):
        with patch("authentication.email_backends.build_opener") as opener:
            self.assertEqual(self.backend.send_messages([]), 0)
            self.message.bcc = ["copy@example.test"]
            with self.assertRaises(EmailDeliveryError):
                self.backend.send_messages([self.message])
            opener.assert_not_called()

    @override_settings(MAILERS={"default": {
        "BACKEND": "authentication.email_backends.BrevoEmailBackend",
        "OPTIONS": {"api_key": "synthetic-private-api-key"},
    }})
    def test_check_command_authenticates_without_sending(self):
        with patch("authentication.email_backends.BrevoEmailBackend._request", return_value=(200, {})) as request:
            output = StringIO()
            call_command("check_reset_email", stdout=output)
            request.assert_called_once_with("smtp/statistics/aggregatedReport?days=1")
            self.assertIn("No message was sent", output.getvalue())
