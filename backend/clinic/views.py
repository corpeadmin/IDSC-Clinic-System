"""
API views for IDSC Clinic System.
Implements complete CRUD endpoints for Students and Health Records,
including relationship endpoints and search/filtering capabilities.
"""

from django.db import models, transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import serializers, viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import (
    Student,
    HealthRecord,
    Medicine,
    DispensingRecord,
    StockTransaction,
)
from .serializers import (
    StudentSerializer,
    StudentDetailSerializer,
    HealthRecordSerializer,
    MedicineSerializer,
    DispensingRecordSerializer,
    StockTransactionSerializer,
    StockInSerializer,
    StockAdjustmentSerializer,
)


class StudentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Students.
    Supports complete CRUD operations:
    - GET /api/students/ : List all students (with optional filtering)
    - POST /api/students/ : Create a new student
    - GET /api/students/<student_id>/ : Retrieve student by ID
    - PUT /api/students/<student_id>/ : Fully update student
    - PATCH /api/students/<student_id>/ : Partially update student
    - DELETE /api/students/<student_id>/ : Delete student
    - GET /api/students/<student_id>/health-records/ : Get all health records for student
    - POST /api/students/<student_id>/health-records/ : Create health record for student
    """
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    lookup_field = 'student_id'
    lookup_value_regex = r'[^/]+'

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return StudentDetailSerializer
        return StudentSerializer

    def get_queryset(self):
        queryset = Student.objects.prefetch_related('health_records').all()
        
        # Query parameter filters
        search = self.request.query_params.get('search', '').strip()
        course = self.request.query_params.get('course', '').strip()
        section = self.request.query_params.get('section', '').strip()
        sex = self.request.query_params.get('sex', '').strip()

        if search:
            filters = (
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(course__icontains=search) |
                Q(section__icontains=search)
            )
            if search.isdigit():
                filters |= Q(student_id=int(search))
            queryset = queryset.filter(filters)
        if course:
            queryset = queryset.filter(course__iexact=course)
        if section:
            queryset = queryset.filter(section__iexact=section)
        if sex:
            queryset = queryset.filter(sex__iexact=sex)

        return queryset

    @action(detail=True, methods=['get', 'post'], url_path='health-records')
    def health_records(self, request, student_id=None):
        """
        Endpoint: /api/students/<student_id>/health-records/
        - GET: Retrieve all health records for this student.
        - POST: Create a new health record for this student.
        """
        student = self.get_object()

        if request.method == 'GET':
            records = student.health_records.all().order_by('-visit', '-health_id')
            serializer = HealthRecordSerializer(records, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        elif request.method == 'POST':
            # Inject student_id into request data if not present
            data = request.data.copy() if hasattr(request.data, 'copy') else dict(request.data)
            data['student_id'] = student.student_id

            serializer = HealthRecordSerializer(data=data)
            if serializer.is_valid():
                serializer.save(student=student)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class HealthRecordViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Health Records.
    Supports complete CRUD operations:
    - GET /api/health-records/ : List all health records (with optional filtering)
    - POST /api/health-records/ : Create a health record
    - GET /api/health-records/<health_id>/ : Retrieve a single record
    - PUT /api/health-records/<health_id>/ : Fully update a record
    - PATCH /api/health-records/<health_id>/ : Partially update a record
    - DELETE /api/health-records/<health_id>/ : Delete a record
    """
    queryset = HealthRecord.objects.select_related('student').all()
    serializer_class = HealthRecordSerializer
    lookup_field = 'health_id'

    def get_queryset(self):
        queryset = HealthRecord.objects.select_related('student').all()

        # Query parameter filters
        student_id = self.request.query_params.get(
            'student_id',
            ''
        ).strip()

        blood_type = self.request.query_params.get(
            'blood_type',
            ''
        ).strip()

        search = self.request.query_params.get(
            'search',
            ''
        ).strip()

        if student_id:
            if student_id.isdigit():
                queryset = queryset.filter(
                    student__student_id=int(student_id)
                )
            else:
                queryset = queryset.filter(
                    student__student_id__exact=student_id
                )

        if blood_type:
            queryset = queryset.filter(
                blood_type__iexact=blood_type
            )

        if search:
            filters = (
                Q(student__first_name__icontains=search) |
                Q(student__last_name__icontains=search) |
                Q(allergies__icontains=search) |
                Q(consultation__icontains=search) |
                Q(medical_history__icontains=search)
            )

            if search.isdigit():
                filters |= Q(
                    student__student_id=int(search)
                )

            queryset = queryset.filter(filters)

        return queryset


class MedicineViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing clinic medicines and inventory.
    """

    queryset = Medicine.objects.all()
    serializer_class = MedicineSerializer

    def get_serializer_class(self):
        if self.action == 'stock_in':
            return StockInSerializer

        if self.action == 'adjust_stock':
            return StockAdjustmentSerializer

        return MedicineSerializer

    def get_queryset(self):
        queryset = Medicine.objects.all()

        search = self.request.query_params.get('search', '').strip()
        low_stock = self.request.query_params.get('low_stock', '').strip()
        active = self.request.query_params.get('active', '').strip()

        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(generic_name__icontains=search)
            )

        if low_stock.lower() in ['true', '1', 'yes']:
            queryset = queryset.filter(
                quantity_in_stock__lte=models.F('reorder_level')
            )

        if active.lower() in ['true', '1', 'yes']:
            queryset = queryset.filter(is_active=True)
        elif active.lower() in ['false', '0', 'no']:
            queryset = queryset.filter(is_active=False)

        return queryset

    @action(detail=False, methods=['get'], url_path='low-stock')
    def low_stock(self, request):
        """
        Return all medicines whose stock is at or below
        the configured reorder level.
        """
        medicines = self.get_queryset().filter(
            quantity_in_stock__lte=models.F('reorder_level')
        )

        serializer = self.get_serializer(medicines, many=True)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    @action(
        detail=True,
        methods=['post'],
        url_path='stock-in',
        permission_classes=[IsAuthenticated],
    )
    def stock_in(self, request, pk=None):
        """
        Add medicine to stock.

        POST /api/medicines/<medicine_id>/stock-in/

        Expected data:
        {
            "quantity": 50,
            "remarks": "New delivery"
        }
        """

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        quantity = serializer.validated_data['quantity']
        remarks = serializer.validated_data.get('remarks', '')

        with transaction.atomic():
            medicine = Medicine.objects.select_for_update().get(
                medicine_id=pk
            )

            previous_stock = medicine.quantity_in_stock
            new_stock = previous_stock + quantity

            medicine.quantity_in_stock = new_stock
            medicine.save(
                update_fields=[
                    'quantity_in_stock',
                    'updated_at',
                ]
            )

            stock_transaction = StockTransaction.objects.create(
                medicine=medicine,
                transaction_type=StockTransaction.TransactionType.STOCK_IN,
                quantity=quantity,
                previous_stock=previous_stock,
                new_stock=new_stock,
                created_by=request.user,
                remarks=remarks,
            )

        return Response(
            StockTransactionSerializer(stock_transaction).data,
            status=status.HTTP_201_CREATED,
        )

    @action(
        detail=True,
        methods=['post'],
        url_path='adjust-stock',
        permission_classes=[IsAuthenticated],
    )
    def adjust_stock(self, request, pk=None):
        """
        Adjust medicine stock.

        POST /api/medicines/<medicine_id>/adjust-stock/

        Expected data:
        {
            "quantity": 3,
            "adjustment": "DECREASE",
            "remarks": "Physical inventory count"
        }

        adjustment must be either:
        - INCREASE
        - DECREASE
        """
        quantity = request.data.get('quantity')
        adjustment = request.data.get(
            'adjustment',
            ''
        ).strip().upper()
        remarks = request.data.get('remarks', '').strip()

        try:
            quantity = int(quantity)
        except (TypeError, ValueError):
            return Response(
                {
                    'quantity': 'Quantity must be a valid integer.'
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if quantity <= 0:
            return Response(
                {
                    'quantity': 'Adjustment quantity must be greater than 0.'
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if adjustment not in ['INCREASE', 'DECREASE']:
            return Response(
                {
                    'adjustment': (
                        'Adjustment must be either '
                        'INCREASE or DECREASE.'
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():
            medicine = Medicine.objects.select_for_update().get(
                medicine_id=pk
            )

            previous_stock = medicine.quantity_in_stock

            if adjustment == 'INCREASE':
                new_stock = previous_stock + quantity
            else:
                if quantity > previous_stock:
                    return Response(
                        {
                            'quantity': (
                                f'Cannot decrease stock by {quantity}. '
                                f'Available stock: {previous_stock}.'
                            )
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                new_stock = previous_stock - quantity

            medicine.quantity_in_stock = new_stock
            medicine.save(
                update_fields=[
                    'quantity_in_stock',
                    'updated_at',
                ]
            )

            stock_transaction = StockTransaction.objects.create(
                medicine=medicine,
                transaction_type=StockTransaction.TransactionType.ADJUSTMENT,
                quantity=quantity,
                previous_stock=previous_stock,
                new_stock=new_stock,
                created_by=request.user,
                remarks=remarks,
            )

        return Response(
            StockTransactionSerializer(stock_transaction).data,
            status=status.HTTP_201_CREATED,
        )


class DispensingRecordViewSet(viewsets.ModelViewSet):
    """
    ViewSet for dispensing medicine to students.

    Dispensing is performed atomically:
    1. Lock the medicine row.
    2. Validate stock.
    3. Deduct stock.
    4. Create dispensing record.
    5. Create stock transaction.
    """

    permission_classes = [IsAuthenticated]

    queryset = DispensingRecord.objects.select_related(
        'medicine',
        'student',
        'dispensed_by',
    ).all()

    serializer_class = DispensingRecordSerializer
    lookup_field = 'dispensing_id'

    def perform_create(self, serializer):
        with transaction.atomic():
            medicine_id = serializer.validated_data['medicine'].medicine_id
            quantity = serializer.validated_data['quantity']

            medicine = Medicine.objects.select_for_update().get(
                medicine_id=medicine_id
            )

            if not medicine.is_active:
                raise serializers.ValidationError({
                    'medicine': 'This medicine is inactive and cannot be dispensed.'
                })

            if quantity > medicine.quantity_in_stock:
                raise serializers.ValidationError({
                    'quantity': (
                        f'Insufficient stock. '
                        f'Available stock: {medicine.quantity_in_stock}.'
                    )
                })

            previous_stock = medicine.quantity_in_stock
            new_stock = previous_stock - quantity

            medicine.quantity_in_stock = new_stock
            medicine.save(update_fields=['quantity_in_stock', 'updated_at'])

            dispensing_record = serializer.save(
                dispensed_by=self.request.user
            )

            StockTransaction.objects.create(
                medicine=medicine,
                transaction_type=StockTransaction.TransactionType.DISPENSE,
                quantity=quantity,
                previous_stock=previous_stock,
                new_stock=new_stock,
                created_by=self.request.user,
                remarks=dispensing_record.remarks,
            )

    def get_queryset(self):
        queryset = self.queryset

        student_id = self.request.query_params.get(
            'student_id',
            ''
        ).strip()

        medicine_id = self.request.query_params.get(
            'medicine_id',
            ''
        ).strip()

        if student_id:
            queryset = queryset.filter(
                student__student_id=student_id
            )

        if medicine_id:
            queryset = queryset.filter(
                medicine__medicine_id=medicine_id
            )

        return queryset


class StockTransactionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only ViewSet for viewing medicine stock history.
    """

    queryset = StockTransaction.objects.select_related(
        'medicine',
        'created_by',
    ).all()

    serializer_class = StockTransactionSerializer
    lookup_field = 'transaction_id'

    def get_queryset(self):
        queryset = self.queryset

        medicine_id = self.request.query_params.get(
            'medicine_id',
            ''
        ).strip()

        transaction_type = self.request.query_params.get(
            'transaction_type',
            ''
        ).strip()

        if medicine_id:
            queryset = queryset.filter(
                medicine__medicine_id=medicine_id
            )

        if transaction_type:
            queryset = queryset.filter(
                transaction_type=transaction_type.upper()
            )

        return queryset