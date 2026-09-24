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
    MedicineStockView,
    MedicineDispensationViewSet,
)
from .views import (
    StudentViewSet,
    HealthRecordViewSet,
    MedicineViewSet,
    DispensingRecordViewSet,
    StockTransactionViewSet,
    MedicineStockView,
    MedicineDispensationViewSet,
    RegistrarStudentView,
)


# Create router and register viewsets
router = DefaultRouter()

router.register(
    r"students",
    StudentViewSet,
    basename="student",
)

router.register(
    r"health-records",
    HealthRecordViewSet,
    basename="health-record",
)

router.register(
    r"medicines",
    MedicineViewSet,
    basename="medicine",
)

router.register(
    r"dispensing-records",
    DispensingRecordViewSet,
    basename="dispensing-record",
)

router.register(
    r"stock-transactions",
    StockTransactionViewSet,
    basename="stock-transaction",
)

router.register(
    r"medicine-dispensations",
    MedicineDispensationViewSet,
    basename="medicine-dispensation",
)


urlpatterns = [
    # DRF router endpoints
    path(
        "",
        include(router.urls),
    ),

    # Clinic-facing medicine stock endpoint
    path(
        "medicine-stock/",
        MedicineStockView.as_view(),
        name="medicine-stock",
    ),

    # Registrar-facing student endpoint
    path(
        "registrar/students/<int:student_id>/",
        RegistrarStudentView.as_view(),
        name="registrar-student",
    ),
]
