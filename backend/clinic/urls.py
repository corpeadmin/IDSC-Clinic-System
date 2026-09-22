"""
URL configuration for the clinic app API endpoints.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    StudentViewSet,
    HealthRecordViewSet,
    StudentPortalHealthRecordViewSet,
    ConsultationViewSet,
    HealthStatusViewSet,
)

# Create router and register viewsets
router = DefaultRouter()
router.register(r'students', StudentViewSet, basename='student')
router.register(r'health-records', HealthRecordViewSet, basename='health-record')
router.register(r'student-portal/health-records', StudentPortalHealthRecordViewSet, basename='student-portal-health-record')
router.register(r'consultations', ConsultationViewSet, basename='consultation')
router.register(r'health-statuses', HealthStatusViewSet, basename='health-status')

urlpatterns = [
    path('', include(router.urls)),
]
