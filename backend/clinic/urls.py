"""
URL configuration for the clinic app API endpoints.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import StudentViewSet, HealthRecordViewSet

# Create router and register viewsets
router = DefaultRouter()
router.register(r'students', StudentViewSet, basename='student')
router.register(r'health-records', HealthRecordViewSet, basename='health-record')

urlpatterns = [
    path('', include(router.urls)),
]
