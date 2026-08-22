"""
Custom API exception handling for the clinic application.
Ensures clean, consistent JSON error responses and prevents raw database exceptions
from leaking to clients.
"""

from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.http import Http404
from rest_framework import status
from rest_framework.exceptions import APIException, ValidationError as DRFValidationError
from rest_framework.response import Response
from rest_framework.views import exception_handler
import logging

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Custom exception handler that intercepts standard and database exceptions
    and returns standardized JSON responses.
    """
    # Call REST framework's default exception handler first to get the standard error response
    response = exception_handler(exc, context)

    if response is not None:
        # Standard DRF exception format
        custom_data = {
            'success': False,
            'status_code': response.status_code,
            'errors': response.data if isinstance(response.data, (dict, list)) else {'detail': str(response.data)},
        }
        response.data = custom_data
        return response

    # Handle Django's built-in ValidationError
    if isinstance(exc, DjangoValidationError):
        if hasattr(exc, 'message_dict'):
            errors = exc.message_dict
        elif hasattr(exc, 'messages'):
            errors = {'non_field_errors': exc.messages}
        else:
            errors = {'detail': str(exc)}
        return Response(
            {
                'success': False,
                'status_code': status.HTTP_400_BAD_REQUEST,
                'errors': errors,
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    # Handle ObjectDoesNotExist / 404
    if isinstance(exc, (ObjectDoesNotExist, Http404)):
        return Response(
            {
                'success': False,
                'status_code': status.HTTP_404_NOT_FOUND,
                'errors': {'detail': 'The requested resource was not found.'},
            },
            status=status.HTTP_404_NOT_FOUND
        )

    # Handle Database Integrity Errors (e.g. duplicate keys, FK violation)
    if isinstance(exc, IntegrityError):
        logger.warning(f"Database IntegrityError encountered: {exc}")
        error_msg = str(exc)
        
        # Provide user-friendly messages for common constraints
        if 'unique constraint' in error_msg.lower() or 'duplicate key' in error_msg.lower() or 'unique' in error_msg.lower():
            detail = 'A record with this identifier already exists.'
            status_code = status.HTTP_400_BAD_REQUEST
        elif 'foreign key constraint' in error_msg.lower() or 'violates foreign key' in error_msg.lower():
            detail = 'Referenced related record does not exist or cannot be modified.'
            status_code = status.HTTP_400_BAD_REQUEST
        else:
            detail = 'A database integrity constraint was violated.'
            status_code = status.HTTP_400_BAD_REQUEST

        return Response(
            {
                'success': False,
                'status_code': status_code,
                'errors': {'detail': detail},
            },
            status=status_code
        )

    # For any other unhandled exception, log and return safe 500 error
    logger.exception("Unhandled server error: %s", exc)
    return Response(
        {
            'success': False,
            'status_code': status.HTTP_500_INTERNAL_SERVER_ERROR,
            'errors': {'detail': 'An unexpected server error occurred.'},
        },
        status=status.HTTP_500_INTERNAL_SERVER_ERROR
    )
