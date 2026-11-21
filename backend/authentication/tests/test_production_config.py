import os, subprocess, sys
from pathlib import Path
from django.test import SimpleTestCase


class ProductionConfigurationTests(SimpleTestCase):
    def database_config(self, **overrides):
        env = os.environ.copy()
        env.update({
            "DEBUG": "False",
            "SECRET_KEY": "private-validation-only-" + ("x" * 64),
            "ALLOWED_HOSTS": "clinic.school.test",
            "PASSWORD_RESET_FRONTEND_URL": "https://clinic.school.test",
            "DB_ENGINE": "django.db.backends.postgresql",
            "DB_HOST": "db.school.test",
            "DB_SSLMODE": "verify-full",
            "DB_SSLROOTCERT": "/private/provider-ca.crt",
        })
        env.update(overrides)
        return subprocess.run(
            [sys.executable, "-c", "import json; from config import settings; print(json.dumps(settings.DATABASES['default'].get('OPTIONS', {})))"],
            cwd=Path(__file__).resolve().parents[2], env=env,
            capture_output=True, text=True,
        )

    def run_config(self, **overrides):
        env = os.environ.copy()
        env.update({"DEBUG": "False", "ALLOWED_HOSTS": "clinic.school.test",
                    "PASSWORD_RESET_FRONTEND_URL": "https://clinic.school.test"})
        env.pop("SECRET_KEY", None)
        env.update(overrides)
        return subprocess.run(
            [sys.executable, "manage.py", "check", "--deploy"],
            cwd=Path(__file__).resolve().parents[2],
            env=env,
            capture_output=True,
            text=True,
        )

    def test_missing_secret_fails_closed(self):
        result = self.run_config()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("private SECRET_KEY", result.stderr)

    def test_valid_explicit_production_configuration(self):
        result = self.run_config(SECRET_KEY="private-validation-only-" + ("x" * 64))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn("security.W", result.stderr)

    def test_wildcard_hosts_fail_closed(self):
        result = self.run_config(
            SECRET_KEY="private-validation-only-" + ("x" * 64), ALLOWED_HOSTS="*"
        )
        self.assertNotEqual(result.returncode, 0)

    def test_hosted_postgres_verifies_certificate_and_hostname(self):
        import json

        result = self.database_config()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout), {
            "sslmode": "verify-full", "sslrootcert": "/private/provider-ca.crt",
        })

    def test_invalid_database_tls_mode_is_rejected(self):
        result = self.database_config(DB_SSLMODE="ignore-errors")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("DB_SSLMODE", result.stderr)

    def test_database_certificate_requires_explicit_tls_mode(self):
        result = self.database_config(DB_SSLMODE="")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("DB_SSLMODE", result.stderr)
