"""Public email recovery using Django's expiring, single-use password tokens."""

import logging
from urllib.parse import urlencode

from django.conf import settings
from django.contrib.auth import get_user_model, logout
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import default_token_generator
from django.core import mail
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from django.db.models import F
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework import serializers
from rest_framework.decorators import api_view, permission_classes, authentication_classes, throttle_classes
from rest_framework.exceptions import APIException, ValidationError, NotFound
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .account_lifecycle import revoke_sessions
from .models import AccessGrant
from .serializers import MessageResponseSerializer
from .throttles import PasswordResetThrottle

User = get_user_model()
logger = logging.getLogger(__name__)
SUCCESS_MESSAGE = "A password-reset link has been sent to your registered email. Check your inbox and spam folder."
EMAIL_NOT_FOUND = "No active Clinic account was found with that email address. Check the address or contact the system Owner."
INVALID_LINK = "This reset link is invalid or has expired. Please request a new one."


class ResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=254)


class ResetConfirmSerializer(serializers.Serializer):
    uid = serializers.RegexField(r"^[A-Za-z0-9_-]+$", max_length=64)
    token = serializers.CharField(max_length=128, trim_whitespace=False)
    new_password = serializers.CharField(max_length=1024, trim_whitespace=False, write_only=True)
    confirm_password = serializers.CharField(max_length=1024, trim_whitespace=False, write_only=True)


class EmailUnavailable(APIException):
    status_code = 503
    default_detail = "Password-reset email is temporarily unavailable. Please try again later or contact the system Owner."
    default_code = "email_unavailable"


@sensitive_post_parameters("email")
@extend_schema(request=ResetRequestSerializer, responses={200: MessageResponseSerializer, 404: OpenApiResponse(description="No eligible account uses this email address."), 503: OpenApiResponse(description="Reset email service unavailable.")},
               description="Send an expiring reset link only to the address saved on an active, recoverable account. Unknown/inactive/unusable addresses return 404. CSRF and rate limits apply.")
@api_view(["POST"])
@authentication_classes([])
@permission_classes([AllowAny])
@throttle_classes([PasswordResetThrottle])
@csrf_protect
def request_password_reset(request):
    serializer = ResetRequestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    users = [user for user in User.objects.filter(
        email__iexact=serializer.validated_data["email"], is_active=True
    ) if user.has_usable_password()]
    if not users:
        raise NotFound(EMAIL_NOT_FOUND)
    if not settings.PASSWORD_RESET_EMAIL_CONFIGURED:
        raise EmailUnavailable()
    try:
        connection = mail.mailers["default"]
        connection.open()
    except Exception as exc:
        logger.warning("Password reset mail transport unavailable (%s).", type(exc).__name__)
        raise EmailUnavailable() from None
    try:
        for user in users:
            query = urlencode({"uid": urlsafe_base64_encode(force_bytes(user.pk)), "token": default_token_generator.make_token(user)})
            link = f"{settings.PASSWORD_RESET_FRONTEND_URL.rstrip('/')}/#reset-password?{query}"
            message = mail.EmailMessage(
                subject="Reset your IDSC Clinic password",
                body=(f"Hello {user.username},\n\nA password reset was requested for your IDSC Clinic account.\n\n"
                      f"Open this link to choose a new password:\n{link}\n\n"
                      "This link expires in 30 minutes and can only be used once. "
                      "If you did not request this, ignore this email. Your password has not changed.\n"),
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[user.email],
            )
            try:
                if connection.send_messages([message]) != 1:
                    raise EmailUnavailable()
            except Exception as exc:
                # Never include email addresses, message bodies, links or credentials.
                logger.warning("Password reset message delivery failed (%s).", type(exc).__name__)
                raise EmailUnavailable() from None
    finally:
        try:
            connection.close()
        except Exception as exc:
            logger.warning("Password reset mail connection close failed (%s).", type(exc).__name__)
    return Response({"message": SUCCESS_MESSAGE})


@sensitive_post_parameters("token", "new_password", "confirm_password")
@extend_schema(request=ResetConfirmSerializer, responses=MessageResponseSerializer,
               description="Redeem a valid reset link once. Applies password validators, revokes all account sessions/JWTs, and requires login afterward. CSRF and rate limits apply.")
@api_view(["POST"])
@authentication_classes([])
@permission_classes([AllowAny])
@throttle_classes([PasswordResetThrottle])
@csrf_protect
def confirm_password_reset(request):
    serializer = ResetConfirmSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data
    try:
        user_id = int(urlsafe_base64_decode(data["uid"]).decode())
        if user_id < 1 or user_id > 9223372036854775807:
            raise ValueError()
    except (ValueError, TypeError, UnicodeDecodeError, OverflowError):
        raise ValidationError({"token": INVALID_LINK}) from None
    with transaction.atomic():
        # Serialize token consumption on SQLite as well as PostgreSQL.
        User.objects.filter(pk=user_id).update(last_login=F("last_login"))
        user = User.objects.select_for_update().filter(pk=user_id, is_active=True).first()
        if not user or not user.has_usable_password() or not default_token_generator.check_token(user, data["token"]):
            raise ValidationError({"token": INVALID_LINK})
        if data["new_password"] != data["confirm_password"]:
            raise ValidationError({"confirm_password": "The passwords do not match."})
        if user.check_password(data["new_password"]):
            raise ValidationError({"new_password": "Choose a password different from your current one."})
        try:
            validate_password(data["new_password"], user)
        except DjangoValidationError as exc:
            raise ValidationError({"new_password": exc.messages}) from None
        user.set_password(data["new_password"])
        user.save(update_fields=["password"])
        revoke_sessions(user.pk)
        AccessGrant.objects.filter(user=user).delete()
    logout(request)
    return Response({"message": "Your password has been reset. Please log in with your new password."})
