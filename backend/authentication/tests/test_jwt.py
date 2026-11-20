from datetime import timedelta

import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.sessions.models import Session
from django.test import Client, TestCase
from django.utils import timezone

from authentication.jwt_auth import signing_key
from authentication.models import AccessGrant

User = get_user_model()
PASSWORD = "DisposableGarden!49183"


class JWTTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.owner = User.objects.create_superuser(username="jwt_owner", password=PASSWORD)
        cls.staff = User.objects.create_user(username="jwt_staff", password=PASSWORD)
        cls.staff.groups.add(Group.objects.get(name="CLINIC_STAFF"))
        cls.admin = User.objects.create_user(username="jwt_admin", password=PASSWORD)
        cls.admin.groups.add(Group.objects.get(name="CLINIC_ADMIN"))

    def login(self, user=None, path="/api/v1/auth/login/"):
        client = Client(enforce_csrf_checks=True)
        csrf = client.get("/api/auth/csrf/").json()["csrfToken"]
        response = client.post(path, {"username": (user or self.staff).username, "password": PASSWORD},
                               content_type="application/json", HTTP_X_CSRFTOKEN=csrf)
        self.assertEqual(response.status_code, 200, response.content)
        return client, response.json()

    def bearer(self, token, path="/api/v1/dashboard/"):
        # No cookies: this must authenticate using the JWT alone.
        return Client().get(path, HTTP_AUTHORIZATION=f"Bearer {token}")

    def claims(self, token):
        return jwt.decode(token, signing_key(), algorithms=["HS256"],
                          audience=settings.JWT_AUDIENCE, issuer=settings.JWT_ISSUER)

    def test_login_issues_real_jwt_and_supports_cookie_free_protected_request(self):
        _, data = self.login()
        self.assertEqual(data["token_type"], "Bearer")
        self.assertEqual(data["expires_in"], 900)
        claims = self.claims(data["access_token"])
        self.assertEqual(claims["sub"], str(self.staff.pk))
        self.assertEqual(claims["role"], "STAFF")
        self.assertNotIn("password", claims)
        self.assertNotIn("session_key", claims)
        self.assertEqual(self.bearer(data["access_token"]).status_code, 200)
        self.assertIn("no-store", self.bearer(data["access_token"])["Cache-Control"])

    def test_legacy_login_still_creates_session_and_also_issues_jwt(self):
        client, data = self.login(path="/api/auth/login/")
        self.assertEqual(client.get("/api/auth/me/").status_code, 200)
        self.assertEqual(self.bearer(data["access_token"]).status_code, 200)

    def test_login_and_cookie_renewal_require_csrf(self):
        self.assertEqual(Client(enforce_csrf_checks=True).post("/api/v1/auth/login/", {}).status_code, 403)
        client, _ = self.login()
        self.assertEqual(client.post("/api/auth/token/", {}, content_type="application/json").status_code, 403)

    def test_renewal_is_session_only_and_does_not_accept_bearer_as_refresh(self):
        client, data = self.login()
        self.assertEqual(Client().post("/api/auth/token/", {}, HTTP_AUTHORIZATION="Bearer " + data["access_token"]).status_code, 401)
        csrf = client.get("/api/auth/csrf/").json()["csrfToken"]
        response = client.post("/api/auth/token/", {}, HTTP_X_CSRFTOKEN=csrf)
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(data["access_token"], response.json()["access_token"])
        self.assertEqual(self.bearer(response.json()["access_token"]).status_code, 200)

    def test_roles_are_enforced_for_bearer_requests(self):
        for user, status in [(self.staff, 403), (self.admin, 403), (self.owner, 200)]:
            _, data = self.login(user)
            self.assertEqual(self.bearer(data["access_token"], "/api/v1/admins/").status_code, status)

    def test_roles_are_read_from_database_not_token_claim(self):
        _, data = self.login(self.admin)
        self.admin.groups.clear()
        self.assertEqual(self.bearer(data["access_token"]).status_code, 403)

    def test_invalid_signature_algorithm_claims_and_expiry_are_rejected(self):
        _, data = self.login()
        original = self.claims(data["access_token"])
        cases = [
            jwt.encode(original, "wrong-signing-key-" * 4, algorithm="HS256"),
            jwt.encode(original, signing_key(), algorithm="HS384"),
            "not-a-jwt",
        ]
        for changes in [
            {"exp": 1}, {"aud": "another-api"}, {"iss": "another-issuer"},
            {"token_type": "refresh"}, {"jti": "bad-uuid"}, {"sub": "not-numeric"},
        ]:
            cases.append(jwt.encode({**original, **changes}, signing_key(), algorithm="HS256"))
        missing = dict(original); missing.pop("exp")
        cases.append(jwt.encode(missing, signing_key(), algorithm="HS256"))
        for token in cases:
            with self.subTest(token_kind=token[:10]):
                response = self.bearer(token)
                self.assertEqual(response.status_code, 401)
                self.assertEqual(response["WWW-Authenticate"], "Bearer")

    def test_invalid_bearer_does_not_fall_back_to_valid_cookie(self):
        client, _ = self.login()
        self.assertEqual(client.get("/api/v1/dashboard/", HTTP_AUTHORIZATION="Bearer malformed").status_code, 401)

    def test_cookie_logout_revokes_issued_tokens(self):
        client, data = self.login()
        csrf = client.get("/api/auth/csrf/").json()["csrfToken"]
        self.assertEqual(client.post("/api/auth/logout/", {}, HTTP_X_CSRFTOKEN=csrf).status_code, 200)
        self.assertEqual(self.bearer(data["access_token"]).status_code, 401)

    def test_bearer_only_logout_revokes_browser_session(self):
        client, data = self.login()
        response = Client().post("/api/auth/logout/", {}, HTTP_AUTHORIZATION="Bearer " + data["access_token"])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(client.get("/api/auth/me/").status_code, 401)
        self.assertEqual(self.bearer(data["access_token"]).status_code, 401)

    def test_deactivation_password_change_session_and_grant_expiry_revoke(self):
        _, data = self.login()
        token = data["access_token"]
        User.objects.filter(pk=self.staff.pk).update(is_active=False)
        self.assertEqual(self.bearer(token).status_code, 401)
        User.objects.filter(pk=self.staff.pk).update(is_active=True)
        self.staff.set_password("DifferentGarden!31927");self.staff.save()
        self.assertEqual(self.bearer(token).status_code, 401)

    def test_expired_or_deleted_server_grant_is_rejected(self):
        _, data = self.login()
        AccessGrant.objects.update(expires_at=timezone.now()-timedelta(seconds=1))
        self.assertEqual(self.bearer(data["access_token"]).status_code, 401)
        AccessGrant.objects.all().delete()
        self.assertEqual(self.bearer(data["access_token"]).status_code, 401)

    def test_session_revocation_is_immediate(self):
        _, data = self.login()
        Session.objects.all().delete()
        self.assertEqual(self.bearer(data["access_token"]).status_code, 401)

    def test_root_health(self):
        self.assertEqual(Client().get("/health").json(), {"status": "ok"})

    def test_cookie_free_bearer_write_and_staff_delete_denial(self):
        _, data = self.login()
        headers = {"HTTP_AUTHORIZATION": "Bearer " + data["access_token"]}
        client = Client(enforce_csrf_checks=True)
        response = client.post("/api/v1/health-records/", {
            "student_id": "2026-0001", "blood_type": "O+",
        }, content_type="application/json", **headers)
        self.assertEqual(response.status_code, 201, response.content)
        path = f"/api/v1/health-records/{response.json()['health_record_id']}/"
        self.assertEqual(client.delete(path, **headers).status_code, 403)

    def test_password_rotation_can_reissue_using_retained_browser_session(self):
        client, first = self.login()
        other_client, other = self.login()
        csrf = client.get("/api/auth/csrf/").json()["csrfToken"]
        response = client.post("/api/auth/password/change/", {
            "current_password": PASSWORD,
            "new_password": "DifferentForest!71923",
            "confirm_password": "DifferentForest!71923",
        }, content_type="application/json", HTTP_X_CSRFTOKEN=csrf,
            HTTP_AUTHORIZATION="Bearer " + first["access_token"])
        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(self.bearer(first["access_token"]).status_code, 401)
        self.assertEqual(self.bearer(other["access_token"]).status_code, 401)
        self.assertEqual(other_client.get("/api/auth/me/").status_code, 401)
        csrf = client.get("/api/auth/csrf/").json()["csrfToken"]
        renewed = client.post("/api/auth/token/", {}, HTTP_X_CSRFTOKEN=csrf)
        self.assertEqual(renewed.status_code, 200, renewed.content)
        self.assertEqual(self.bearer(renewed.json()["access_token"]).status_code, 200)
