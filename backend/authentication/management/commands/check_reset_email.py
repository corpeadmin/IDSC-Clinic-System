from django.conf import settings
from django.core import mail
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Check password-reset email transport without sending a message or printing credentials."

    def handle(self, *args, **options):
        backend = settings.MAILERS["default"]["BACKEND"]
        if backend != "django.core.mail.backends.smtp.EmailBackend":
            self.stdout.write("Local/test email backend is active. Messages do not reach Gmail inboxes. Configure private SMTP settings first.")
            return
        if not settings.PASSWORD_RESET_EMAIL_CONFIGURED:
            raise CommandError("SMTP sender credentials are missing. Complete backend/.env; do not share the App Password in chat.")
        try:
            with mail.mailers["default"]:
                pass
        except Exception as exc:
            raise CommandError(f"SMTP connection/authentication failed ({type(exc).__name__}). Check private settings and network access.") from None
        self.stdout.write(self.style.SUCCESS("SMTP connection and authentication succeeded. No message was sent."))
