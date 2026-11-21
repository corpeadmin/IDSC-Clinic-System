"""HTTPS delivery for deployments where SMTP ports are unavailable."""

import json
from email.utils import parseaddr
from urllib.error import HTTPError, URLError
from urllib.request import HTTPRedirectHandler, Request, build_opener

from django.core.exceptions import ValidationError
from django.core.mail.backends.base import BaseEmailBackend
from django.core.validators import validate_email


class EmailDeliveryError(Exception):
    """Sanitized transport error: never include credentials or message content."""


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        # Never forward the API key or reset link to another endpoint.
        return None


class BrevoEmailBackend(BaseEmailBackend):
    """Send plaintext transactional recovery messages through Brevo's API."""

    def __init__(self, *, api_key="", timeout=10, **kwargs):
        super().__init__(**kwargs)
        self.api_key = api_key
        self.timeout = timeout

    def open(self):
        if not self.api_key:
            raise EmailDeliveryError("Email API credentials are missing.")

    def _request(self, path, payload=None):
        self.open()
        request = Request(
            "https://api.brevo.com/v3/" + path,
            data=None if payload is None else json.dumps(payload).encode("utf-8"),
            headers={"api-key": self.api_key, "Accept": "application/json",
                     "Content-Type": "application/json"},
            method="GET" if payload is None else "POST",
        )
        try:
            with build_opener(NoRedirect).open(request, timeout=self.timeout) as response:
                status = response.status
                content = response.read(1_000_001)
            if len(content) > 1_000_000:
                raise EmailDeliveryError("Email provider response is invalid.")
            result = json.loads(content)
            if not isinstance(result, dict):
                raise ValueError()
            return status, result
        except (HTTPError, URLError, OSError, ValueError):
            raise EmailDeliveryError("Email provider request failed.") from None

    def check_connection(self):
        # Keep diagnostics within the restricted transactional-email scope.
        status, _ = self._request("smtp/statistics/aggregatedReport?days=1")
        if status != 200:
            raise EmailDeliveryError("Email provider authentication failed.")

    @staticmethod
    def _address(value):
        name, address = parseaddr(value)
        try:
            validate_email(address)
        except ValidationError:
            raise EmailDeliveryError("A valid email address is required.") from None
        return {"email": address, **({"name": name} if name else {})}

    def send_messages(self, email_messages):
        sent = 0
        for message in email_messages or []:
            if not message.to:
                continue
            # Reject unsupported content rather than silently dropping it.
            if message.cc or message.bcc or message.attachments or getattr(message, "alternatives", []):
                raise EmailDeliveryError("Unsupported recovery email content.")
            payload = {
                "sender": self._address(message.from_email),
                "to": [self._address(address) for address in message.to],
                "subject": message.subject,
                "textContent": message.body,
            }
            status, result = self._request("smtp/email", payload)
            if status != 201 or not isinstance(result.get("messageId"), str) or not result["messageId"]:
                raise EmailDeliveryError("Email provider did not accept the message.")
            sent += 1
        return sent
