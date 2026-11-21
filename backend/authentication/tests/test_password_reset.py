import re
from datetime import datetime, timedelta
from unittest.mock import patch
from urllib.parse import parse_qs, urlsplit

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sessions.models import Session
from django.core import mail
from django.core.cache import cache
from django.test import Client, TestCase, override_settings

from authentication.models import AccessGrant

User = get_user_model()
OLD = "DisposableGarden!49183"
NEW = "DifferentForest!71923"
REQUEST = "/api/auth/password/reset/"
CONFIRM = "/api/auth/password/reset/confirm/"
MAILERS = {"default": {"BACKEND": "django.core.mail.backends.locmem.EmailBackend"}}


@override_settings(MAILERS=MAILERS, PASSWORD_RESET_EMAIL_CONFIGURED=True,
                   PASSWORD_RESET_FRONTEND_URL="https://clinic.example.test")
class PasswordResetTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.owner = User.objects.create_superuser(username="reset_owner", email="owner@example.test", password=OLD)
        cls.staff = User.objects.create_user(username="reset_staff", email="staff@example.test", password=OLD)
        cls.staff.groups.add(Group.objects.get(name="CLINIC_STAFF"))

    def setUp(self):
        cache.clear()
        self.client = Client(enforce_csrf_checks=True)

    def post(self, path, data, client=None, **headers):
        client = client or self.client
        token = client.get("/api/auth/csrf/").json()["csrfToken"]
        return client.post(path, data, content_type="application/json", HTTP_X_CSRFTOKEN=token, **headers)

    def link(self, user=None):
        response = self.post(REQUEST, {"email": (user or self.staff).email})
        self.assertEqual(response.status_code, 200, response.content)
        url = re.search(r"https://[^\s]+", mail.outbox[-1].body).group()
        fragment = urlsplit(url).fragment
        return {key: value[0] for key, value in parse_qs(fragment.split("?", 1)[1]).items()}

    def reset(self, link, **overrides):
        return self.post(CONFIRM, {**link, "new_password": NEW, "confirm_password": NEW, **overrides})

    def test_known_email_receives_trusted_origin_link_without_passwords(self):
        link = self.link()
        message = mail.outbox[0]
        self.assertEqual(message.to, [self.staff.email])
        self.assertIn("https://clinic.example.test/#reset-password?", message.body)
        self.assertIn("30 minutes", message.body)
        self.assertNotIn(OLD, message.body)
        self.assertTrue(default_token_generator.check_token(self.staff, link["token"]))

    def test_success_hashes_password_and_link_cannot_be_reused(self):
        link = self.link()
        response = self.reset(link)
        self.assertEqual(response.status_code, 200, response.content)
        self.staff.refresh_from_db()
        self.assertTrue(self.staff.check_password(NEW))
        self.assertFalse(self.staff.check_password(OLD))
        self.assertEqual(self.reset(link).status_code, 400)
        self.assertNotIn("access_token", response.json())

    def test_owner_can_recover_without_losing_ownership(self):
        self.assertEqual(self.reset(self.link(self.owner)).status_code, 200)
        self.owner.refresh_from_db()
        self.assertTrue(self.owner.is_superuser and self.owner.is_active)

    def test_unknown_inactive_unusable_addresses_return_not_found_without_mail(self):
        User.objects.create_user(username="inactive_reset", email="inactive@example.test", password=OLD, is_active=False)
        User.objects.create_user(username="unusable_reset", email="unusable@example.test", password=None)
        with patch("authentication.password_reset.mail.mailers.__class__.__getitem__") as transport:
            for value in ["unknown@example.test", "inactive@example.test", "unusable@example.test"]:
                response = self.post(REQUEST, {"email": value})
                self.assertEqual(response.status_code, 404)
                self.assertIn("No active Clinic account", response.json()["detail"])
            transport.assert_not_called()

    def test_email_match_is_case_insensitive_and_trimmed(self):
        self.assertEqual(self.post(REQUEST, {"email": "  STAFF@EXAMPLE.TEST  "}).status_code, 200)
        self.assertEqual(len(mail.outbox), 1)

    def test_invalid_email_is_rejected(self):
        self.assertEqual(self.post(REQUEST, {"email": "not-an-email"}).status_code, 400)

    def test_both_public_posts_require_csrf(self):
        self.assertEqual(self.client.post(REQUEST, {}).status_code, 403)
        self.assertEqual(self.client.post(CONFIRM, {}).status_code, 403)

    def test_mismatch_weak_and_reused_password_leave_link_usable(self):
        link = self.link()
        self.assertEqual(self.reset(link, confirm_password="mismatch").status_code, 400)
        self.assertEqual(self.reset(link, new_password="password", confirm_password="password").status_code, 400)
        self.assertEqual(self.reset(link, new_password=OLD, confirm_password=OLD).status_code, 400)
        self.assertEqual(self.reset(link).status_code, 200)

    def test_expired_link_is_rejected(self):
        link = self.link()
        with patch.object(default_token_generator, "_now", return_value=datetime.now() + timedelta(hours=1)):
            self.assertEqual(self.reset(link).status_code, 400)

    def test_tampered_token_and_uid_are_rejected(self):
        link = self.link()
        self.assertEqual(self.reset({**link, "token": "tampered"}).status_code, 400)
        self.assertEqual(self.reset({**link, "uid": "not_a_user"}).status_code, 400)
        self.assertEqual(self.reset({**link, "uid": "OTk5OTk5OTk5OTk5OTk5OTk5OTk5OTk5"}).status_code, 400)

    def test_deactivation_or_email_change_invalidates_link(self):
        link = self.link()
        User.objects.filter(pk=self.staff.pk).update(is_active=False)
        self.assertEqual(self.reset(link).status_code, 400)
        User.objects.filter(pk=self.staff.pk).update(is_active=True, email="changed@example.test")
        self.assertEqual(self.reset(link).status_code, 400)

    def test_all_sessions_and_bearer_grants_are_revoked(self):
        browser = Client(enforce_csrf_checks=True)
        login = self.post("/api/v1/auth/login/", {"username": self.staff.username, "password": OLD}, client=browser)
        access = login.json()["access_token"]
        link = self.link()
        self.assertEqual(self.reset(link).status_code, 200)
        self.assertFalse(AccessGrant.objects.filter(user=self.staff).exists())
        self.assertEqual(browser.get("/api/auth/me/").status_code, 401)
        self.assertEqual(Client().get("/api/v1/dashboard/", HTTP_AUTHORIZATION="Bearer " + access).status_code, 401)
        other = self.post("/api/v1/auth/login/", {"username": self.staff.username, "password": NEW})
        self.assertEqual(other.status_code, 200)

    @override_settings(ALLOWED_HOSTS=["testserver", "attacker.invalid"])
    def test_host_header_cannot_change_email_link(self):
        self.post(REQUEST, {"email": self.staff.email}, HTTP_HOST="attacker.invalid")
        self.assertIn("https://clinic.example.test/", mail.outbox[-1].body)
        self.assertNotIn("attacker.invalid", mail.outbox[-1].body)

    @override_settings(PASSWORD_RESET_EMAIL_CONFIGURED=False)
    def test_unconfigured_mail_is_503_for_known_and_404_for_unknown(self):
        self.assertEqual(self.post(REQUEST, {"email": self.staff.email}).status_code, 503)
        self.assertEqual(self.post(REQUEST, {"email": "unknown@example.test"}).status_code, 404)

    def test_mail_outage_reports_unavailable_without_private_details(self):
        with patch("authentication.password_reset.mail.mailers.__class__.__getitem__", side_effect=OSError("private detail")):
            response = self.post(REQUEST, {"email": self.staff.email})
            self.assertEqual(response.status_code, 503)
            self.assertNotIn("private detail", response.content.decode())

    def test_request_rate_is_limited(self):
        for _ in range(10):
            self.assertEqual(self.post(REQUEST, {"email": "unknown@example.test"}).status_code, 404)
        self.assertEqual(self.post(REQUEST, {"email": "unknown@example.test"}).status_code, 429)

    def test_delivery_failure_never_reports_a_sent_message(self):
        for failure in ("exception", "zero"):
            with self.subTest(failure=failure), patch("authentication.password_reset.mail.mailers.__class__.__getitem__") as transport:
                if failure == "exception":
                    transport.return_value.send_messages.side_effect = OSError("private provider detail")
                else:
                    transport.return_value.send_messages.return_value = 0
                response = self.post(REQUEST, {"email": self.staff.email})
                self.assertEqual(response.status_code, 503)
                self.assertNotIn("private provider detail", response.content.decode())

    @override_settings(MAILERS={"default": {
        "BACKEND": "authentication.email_backends.BrevoEmailBackend",
        "OPTIONS": {"api_key": "synthetic-private-api-key"},
    }})
    def test_https_backend_sends_to_registered_recipient_and_reports_provider_outage(self):
        with patch("authentication.email_backends.BrevoEmailBackend._request", return_value=(201, {"messageId": "synthetic-message"})) as provider:
            response = self.post(REQUEST, {"email": self.staff.email})
            self.assertEqual(response.status_code, 200)
            payload = provider.call_args.args[1]
            self.assertEqual(payload["to"], [{"email": self.staff.email}])
            self.assertIn("https://clinic.example.test/#reset-password?", payload["textContent"])
        with patch("authentication.email_backends.BrevoEmailBackend._request", side_effect=OSError("private-provider-detail")):
            response = self.post(REQUEST, {"email": self.staff.email})
            self.assertEqual(response.status_code, 503)
            self.assertNotIn("private-provider-detail", response.content.decode())

    @override_settings(MAILERS={"default": {
        "BACKEND": "django.core.mail.backends.smtp.EmailBackend",
        "OPTIONS": {"host": "smtp.gmail.com", "port": 587,
                    "username": "synthetic-sender@example.test",
                    "password": "synthetic-app-password", "use_tls": True},
    }})
    def test_smtp_uses_tls_authentication_and_registered_recipient(self):
        with patch("django.core.mail.backends.smtp.smtplib.SMTP") as smtp:
            smtp.return_value.sendmail.return_value = {}
            response = self.post(REQUEST, {"email": self.staff.email})
            self.assertEqual(response.status_code, 200)
            smtp.assert_called_once()
            self.assertEqual(smtp.call_args.args, ("smtp.gmail.com", 587))
            smtp.return_value.starttls.assert_called_once()
            smtp.return_value.login.assert_called_once_with(
                "synthetic-sender@example.test", "synthetic-app-password"
            )
            args = smtp.return_value.sendmail.call_args.args
            self.assertEqual(args[1], [self.staff.email])
