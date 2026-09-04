"""
URL configuration for IDSC Clinic System backend.
"""

from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse


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
            'admin': '/admin/',
        }
    })


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('authentication.urls')),
    path('api/', include('clinic.urls')),
    path('', api_root_view, name='api-root'),
]

from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('authentication.urls')),
    path('api/', include('clinic.urls')),
    path('', api_root_view, name='api-root'),

    # OpenAPI schema + docs
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]       