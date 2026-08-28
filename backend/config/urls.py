"""
URL configuration for IDSC Clinic System backend.
"""

from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)


def api_root_view(request):
    """Simple health / discovery endpoint for the backend API."""
    return JsonResponse({
        'name': 'IDSC Clinic System API',
        'version': '1.0.0',
        'status': 'healthy',
        'endpoints': {
            'students': '/api/students/',
            'health_records': '/api/health-records/',
            'student_health_records': '/api/students/<student_id>/health-records/',
            'schema': '/api/schema/',
            'docs': '/api/docs/',
            'redoc': '/api/redoc/',
            'admin': '/admin/',
        }
    })


urlpatterns = [
    path('admin/', admin.site.urls),
    # OpenAPI and Swagger documentation endpoints
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    # API endpoints
    path('api/', include('clinic.urls')),
    path('', api_root_view, name='api-root'),
]
