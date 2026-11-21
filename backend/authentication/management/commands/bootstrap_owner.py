"""Provision a hosted Owner before opening the public web listener."""

import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from authentication.models import OwnerRegistration
from authentication.serializers import OwnerRegisterSerializer


class Command(BaseCommand):
    help = "Create the first hosted Owner from private INITIAL_OWNER_* variables; never changes an existing Owner."

    def handle(self, *args, **options):
        if os.environ.get("REQUIRE_OWNER_BEFORE_SERVING", "False").lower() not in ("true", "1", "yes"):
            return
        User = get_user_model()
        with transaction.atomic():
            # Match first-run API locking, including SQLite's write-lock behavior.
            if not OwnerRegistration.objects.filter(pk=1).update(id=1):
                OwnerRegistration.objects.create(pk=1)
            state = OwnerRegistration.objects.select_for_update().get(pk=1)
            existing = User.objects.filter(is_superuser=True, is_active=True).first()
            if existing:
                self.stdout.write("An active Owner already exists; credentials were not changed.")
                return
            if state.owner_id is not None or User.objects.filter(is_superuser=True).exists():
                raise CommandError("Owner state requires private operator recovery; no account was changed.")
            username = os.environ.get("INITIAL_OWNER_USERNAME", "")
            password = os.environ.get("INITIAL_OWNER_PASSWORD", "")
            email = os.environ.get("INITIAL_OWNER_EMAIL", "")
            if not all([username, password, email]):
                raise CommandError("Set private INITIAL_OWNER_USERNAME, INITIAL_OWNER_PASSWORD and INITIAL_OWNER_EMAIL before first public startup.")
            serializer = OwnerRegisterSerializer(data={
                "username": username, "password": password,
                "confirm_password": password, "email": email,
            })
            if not serializer.is_valid():
                # Do not echo validation values or private environment contents.
                raise CommandError("Initial Owner details failed validation. Check the username, email and password-strength rules privately.")
            data = dict(serializer.validated_data)
            data.pop("confirm_password")
            owner = User.objects.create_superuser(**data)
            state.owner = owner
            state.save(update_fields=["owner"])
        self.stdout.write(self.style.SUCCESS("Initial hosted Owner created; public registration is closed. Remove INITIAL_OWNER_* secrets after verification."))
