from django.contrib.auth import authenticate, login, logout
from django.middleware.csrf import get_token

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response


@api_view(["GET"])
@permission_classes([AllowAny])
def csrf_token(request):
    """
    Return a CSRF token and ensure the CSRF cookie is set.
    """
    token = get_token(request)

    return Response({
        "csrfToken": token
    })


@api_view(["POST"])
@permission_classes([AllowAny])
def login_view(request):
    """
    Authenticate a user and create a Django session.
    """
    username = request.data.get("username")
    password = request.data.get("password")

    if not username or not password:
        return Response(
            {
                "detail": "Username and password are required."
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    user = authenticate(
        request,
        username=username,
        password=password,
    )

    if user is None:
        return Response(
            {
                "detail": "Invalid username or password."
            },
            status=status.HTTP_401_UNAUTHORIZED,
        )

    if not user.is_active:
        return Response(
            {
                "detail": "This account is inactive."
            },
            status=status.HTTP_403_FORBIDDEN,
        )

    login(request, user)

    return Response(
        {
            "message": "Login successful.",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "is_staff": user.is_staff,
            },
        },
        status=status.HTTP_200_OK,
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """
    Log out the current authenticated user and destroy the session.
    """
    logout(request)

    return Response(
        {
            "message": "Logout successful."
        },
        status=status.HTTP_200_OK,
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def me_view(request):
    """
    Return information about the currently authenticated user.
    """
    user = request.user

    return Response(
        {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "is_staff": user.is_staff,
        },
        status=status.HTTP_200_OK,
    )