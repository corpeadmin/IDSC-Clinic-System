"""Short-lived JWTs backed by revocable login sessions and current DB roles."""

from datetime import timedelta
from uuid import UUID

import jwt
from django.conf import settings
from django.contrib.sessions.models import Session
from django.utils import timezone
from django.utils.crypto import constant_time_compare, salted_hmac
from rest_framework.authentication import BaseAuthentication, get_authorization_header
from rest_framework.exceptions import AuthenticationFailed

from .models import AccessGrant


def signing_key():
    # Separate key material from Django session signing, without another secret to manage.
    return salted_hmac("clinic.jwt.signing", "access-v1", algorithm="sha256").hexdigest()


def issue_access(request, user):
    from .serializers import get_user_role

    now = timezone.now()
    expires = now + timedelta(seconds=settings.JWT_ACCESS_SECONDS)
    # New login sessions must be saved before their first bearer request arrives.
    if request.session.modified or not request.session.session_key:
        request.session.save()
    grant = AccessGrant.objects.create(
        user=user, session_key=request.session.session_key, expires_at=expires
    )
    claims = {
        "sub": str(user.pk),
        "jti": str(grant.pk),
        "role": get_user_role(user),
        "iss": settings.JWT_ISSUER,
        "aud": settings.JWT_AUDIENCE,
        "iat": now,
        "nbf": now,
        "exp": expires,
        "token_type": "access",
    }
    return {
        "access_token": jwt.encode(claims, signing_key(), algorithm="HS256"),
        "token_type": "Bearer",
        "expires_in": settings.JWT_ACCESS_SECONDS,
    }


class ClinicJWTAuthentication(BaseAuthentication):
    def authenticate_header(self, request):
        # Retain the legacy unauthenticated-session challenge for existing clients.
        return "Bearer" if get_authorization_header(request) else "Session"

    def authenticate(self, request):
        header = get_authorization_header(request).split()
        if not header:
            return None
        if len(header) != 2 or header[0].lower() != b"bearer":
            raise AuthenticationFailed("Use Authorization: Bearer <access token>.")
        try:
            claims = jwt.decode(
                header[1],
                signing_key(),
                algorithms=["HS256"],
                issuer=settings.JWT_ISSUER,
                audience=settings.JWT_AUDIENCE,
                options={"require": ["sub", "jti", "iss", "aud", "iat", "nbf", "exp", "token_type"]},
            )
            if claims["token_type"] != "access":
                raise ValueError("Wrong token type")
            grant = AccessGrant.objects.select_related("user").get(
                pk=UUID(claims["jti"]),
                user_id=int(claims["sub"]),
                expires_at__gt=timezone.now(),
            )
            session = Session.objects.get(
                session_key=grant.session_key,
                expire_date__gt=timezone.now(),
            ).get_decoded()
            user = grant.user
            if (
                not user.is_active
                or str(session.get("_auth_user_id")) != str(user.pk)
                or not constant_time_compare(
                    session.get("_auth_user_hash", ""), user.get_session_auth_hash()
                )
            ):
                raise ValueError("Login revoked")
        except (
            jwt.InvalidTokenError, ValueError, TypeError, OverflowError,
            AccessGrant.DoesNotExist, Session.DoesNotExist,
        ):
            raise AuthenticationFailed(
                "Your access token is invalid, expired or revoked."
            ) from None
        # Never authorize with role claims: permissions read this fresh DB user.
        return user, grant
