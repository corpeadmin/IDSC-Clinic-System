from django.core.management.base import BaseCommand
from django.utils import timezone

from authentication.models import AccessGrant


class Command(BaseCommand):
    help = "Remove expired JWT receipts without touching active logins."

    def handle(self, *args, **options):
        count, _ = AccessGrant.objects.filter(expires_at__lte=timezone.now()).delete()
        self.stdout.write(f"Removed {count} expired access grants.")
