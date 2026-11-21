from django.conf import settings
from django.db import models
import uuid


class OwnerRegistration(models.Model):
    """A permanent first-run latch: registration never reopens after completion."""
    id = models.PositiveSmallIntegerField(primary_key=True, default=1, editable=False)
    owner = models.OneToOneField(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.PROTECT, related_name="owner_registration")

    class Meta:
        constraints = [models.CheckConstraint(condition=models.Q(id=1), name="single_owner_registration_row")]


class AccessGrant(models.Model):
    """Revocable JWT receipt; the session identifier never leaves the server."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    session_key = models.CharField(max_length=40)
    expires_at = models.DateTimeField(db_index=True)
