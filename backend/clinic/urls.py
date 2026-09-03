"""
URL configuration for the clinic app API endpoints.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    StudentViewSet,
    HealthRecordViewSet,
    MedicineViewSet,
    DispensingRecordViewSet,
    StockTransactionViewSet,
)

# Create router and register viewsets
router = DefaultRouter()
router.register(r'students', StudentViewSet, basename='student')
router.register(r'health-records', HealthRecordViewSet, basename='health-record')
router.register(r'medicines', MedicineViewSet, basename='medicine')
router.register(
    r'dispensing-records',
    DispensingRecordViewSet,
    basename='dispensing-record'
)
router.register(
    r'stock-transactions',
    StockTransactionViewSet,
    basename='stock-transaction'
)

urlpatterns = [
    path('', include(router.urls)),
]
