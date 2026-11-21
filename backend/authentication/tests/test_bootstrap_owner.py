import os
from io import StringIO
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.management import call_command, CommandError
from django.test import TestCase

from authentication.owner_setup import registration_available


class HostedOwnerTests(TestCase):
    def configure(self, **changes):
        values = {
            "REQUIRE_OWNER_BEFORE_SERVING": "True",
            "INITIAL_OWNER_USERNAME": "hosted_owner",
            "INITIAL_OWNER_PASSWORD": "SyntheticGarden!419837",
            "INITIAL_OWNER_EMAIL": "owner@example.test",
        }
        values.update(changes)
        return patch.dict(os.environ, values)

    def test_creates_one_owner_closes_registration_and_never_rotates_existing_password(self):
        output = StringIO()
        with self.configure():
            call_command("bootstrap_owner", stdout=output)
        user = get_user_model().objects.get(is_superuser=True)
        self.assertEqual(user.email, "owner@example.test")
        self.assertTrue(user.check_password("SyntheticGarden!419837"))
        self.assertFalse(registration_available())
        with self.configure(INITIAL_OWNER_PASSWORD="OtherSynthetic!715893"):
            call_command("bootstrap_owner", stdout=output)
        user.refresh_from_db()
        self.assertTrue(user.check_password("SyntheticGarden!419837"))
        self.assertEqual(get_user_model().objects.count(), 1)
        self.assertNotIn("SyntheticGarden", output.getvalue())
        self.assertNotIn(user.email, output.getvalue())

    def test_missing_or_weak_credentials_fail_without_creating_account(self):
        for value in ["", "password"]:
            with self.subTest(value=value), self.configure(INITIAL_OWNER_PASSWORD=value):
                with self.assertRaises(CommandError):
                    call_command("bootstrap_owner", stdout=StringIO())
                self.assertEqual(get_user_model().objects.count(), 0)

    def test_default_profile_keeps_first_run_registration(self):
        with self.configure(REQUIRE_OWNER_BEFORE_SERVING="False"):
            call_command("bootstrap_owner", stdout=StringIO())
        self.assertTrue(registration_available())
        self.assertEqual(get_user_model().objects.count(), 0)
