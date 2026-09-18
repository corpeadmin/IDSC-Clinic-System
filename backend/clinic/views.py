"""
API views for IDSC Clinic System.
Implements complete CRUD endpoints for Students and Health Records,
including relationship endpoints and search/filtering capabilities.
"""

from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from .models import Student, HealthRecord, HealthStatus
from .serializers import (
    StudentSerializer,
    StudentDetailSerializer,
    HealthRecordSerializer,
    HealthStatusSerializer,
)


@extend_schema_view(
    list=extend_schema(
        tags=['Students'],
        summary="List all students",
        description="Retrieve a list of all students with optional search by student ID.",
        parameters=[
            OpenApiParameter(
                name='search',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Search keyword matching student ID'
            ),
        ],
    ),
    retrieve=extend_schema(
        tags=['Students'],
        summary="Retrieve student details",
        description="Retrieve complete details for a specific student by student_id, including full nested health records history.",
        responses={200: StudentDetailSerializer},
    ),
    create=extend_schema(
        tags=['Students'],
        summary="Create a new student",
        description="Register a new student record in the IDSC Clinic System with an externally supplied student_id.",
        request=StudentSerializer,
        responses={201: StudentSerializer},
    ),
    update=extend_schema(
        tags=['Students'],
        summary="Update a student",
        description="Update fields of an existing student record.",
        request=StudentSerializer,
        responses={200: StudentSerializer},
    ),
    partial_update=extend_schema(
        tags=['Students'],
        summary="Partially update a student",
        description="Partially update one or more fields of an existing student record.",
        request=StudentSerializer,
        responses={200: StudentSerializer},
    ),
    destroy=extend_schema(
        tags=['Students'],
        summary="Delete a student",
        description="Delete an existing student and all associated health records.",
        responses={204: None},
    ),
)
class StudentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Students.
    Supports complete CRUD operations:
    - GET /api/students/ : List all students (with optional search by student_id)
    - POST /api/students/ : Create a new student with externally supplied student_id
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
        
        search = self.request.query_params.get('search', '').strip()

        if search:
            if search.isdigit():
                queryset = queryset.filter(student_id=int(search))

        return queryset

    @extend_schema(
        methods=['GET'],
        tags=['Students'],
        summary="List health records for a student",
        description="Retrieve all health records and clinic consultations for a specific student, ordered by visit date descending.",
        responses={200: HealthRecordSerializer(many=True)},
    )
    @extend_schema(
        methods=['POST'],
        tags=['Students'],
        summary="Create health record for a student",
        description="Create a new clinic consultation / health record for the specified student.",
        request=HealthRecordSerializer,
        responses={201: HealthRecordSerializer},
    )
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


@extend_schema_view(
    list=extend_schema(
        tags=['Health Records'],
        summary="List all health records",
        description="Retrieve a list of all health records with optional filtering by student ID, blood type, or search keyword.",
        parameters=[
            OpenApiParameter(
                name='student_id',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Filter health records for a specific student by student ID'
            ),
            OpenApiParameter(
                name='blood_type',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                enum=['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-', 'Unknown'],
                description='Filter health records by blood type'
            ),
            OpenApiParameter(
                name='search',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Search keyword matching allergies, consultation notes, medical history, or student ID'
            ),
        ],
    ),
    retrieve=extend_schema(
        tags=['Health Records'],
        summary="Retrieve a health record",
        description="Retrieve details of a specific health record by health_id.",
        responses={200: HealthRecordSerializer},
    ),
    create=extend_schema(
        tags=['Health Records'],
        summary="Create a health record",
        description="Create a new clinic consultation / health record associated with a student.",
        request=HealthRecordSerializer,
        responses={201: HealthRecordSerializer},
    ),
    update=extend_schema(
        tags=['Health Records'],
        summary="Update a health record",
        description="Update all fields of an existing health record.",
        request=HealthRecordSerializer,
        responses={200: HealthRecordSerializer},
    ),
    partial_update=extend_schema(
        tags=['Health Records'],
        summary="Partially update a health record",
        description="Partially update one or more fields of an existing health record.",
        request=HealthRecordSerializer,
        responses={200: HealthRecordSerializer},
    ),
    destroy=extend_schema(
        tags=['Health Records'],
        summary="Delete a health record",
        description="Delete an existing health record by health_id.",
        responses={204: None},
    ),
)
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
        student_id = self.request.query_params.get('student_id', '').strip()
        blood_type = self.request.query_params.get('blood_type', '').strip()
        search = self.request.query_params.get('search', '').strip()

        if student_id:
            if student_id.isdigit():
                queryset = queryset.filter(student__student_id=int(student_id))
            else:
                queryset = queryset.filter(student__student_id__exact=student_id)
        if blood_type:
            queryset = queryset.filter(blood_type__iexact=blood_type)
        if search:
            filters = (
                Q(allergies__icontains=search) |
                Q(consultation__icontains=search) |
                Q(medical_history__icontains=search)
            )
            if search.isdigit():
                filters |= Q(student__student_id=int(search))
            queryset = queryset.filter(filters)

        return queryset


@extend_schema_view(
    list=extend_schema(
        tags=['Student Portal'],
        summary="List all health records for the Student Portal",
        description="View-only endpoint for the Student Portal System. Returns all available health-record data.",
        responses={200: HealthRecordSerializer(many=True)},
    ),
    retrieve=extend_schema(
        tags=['Student Portal'],
        operation_id='student_portal_health_records_retrieve',
        summary="Retrieve a specific student's health records",
        description="View-only endpoint for the Student Portal System. Returns the health records associated with the specified student_id.",
        responses={200: HealthRecordSerializer(many=True)},
    ),
)
class StudentPortalHealthRecordViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only ViewSet exposing health-record data to the external Student Portal System.
    - GET /api/student-portal/health-records/ : List all health records
    - GET /api/student-portal/health-records/<student_id>/ : List all health records for a specific student
    This API is view-only; it does not expose create, update, or delete operations.
    """
    queryset = HealthRecord.objects.select_related('student').all()
    serializer_class = HealthRecordSerializer
    lookup_field = 'student_id'
    lookup_value_regex = r'[^/]+'

    def retrieve(self, request, *args, **kwargs):
        student = get_object_or_404(Student, student_id=kwargs.get('student_id'))
        records = student.health_records.all().order_by('-visit', '-health_id')
        serializer = self.get_serializer(records, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema_view(
    list=extend_schema(
        tags=['Health Status'],
        summary="List all health statuses",
        description="Retrieve a list of all health status records. Consumed by the external Faculty System.",
        responses={200: HealthStatusSerializer(many=True)},
    ),
    retrieve=extend_schema(
        tags=['Health Status'],
        summary="Retrieve a health status",
        description="Retrieve details of a specific health status record by status_id.",
        responses={200: HealthStatusSerializer},
    ),
    create=extend_schema(
        tags=['Health Status'],
        summary="Create a health status",
        description="Create a new health status record associated with a student.",
        request=HealthStatusSerializer,
        responses={201: HealthStatusSerializer},
    ),
    update=extend_schema(
        tags=['Health Status'],
        summary="Update a health status",
        description="Update all fields of an existing health status record.",
        request=HealthStatusSerializer,
        responses={200: HealthStatusSerializer},
    ),
    partial_update=extend_schema(
        tags=['Health Status'],
        summary="Partially update a health status",
        description="Partially update one or more fields of an existing health status record.",
        request=HealthStatusSerializer,
        responses={200: HealthStatusSerializer},
    ),
    destroy=extend_schema(
        tags=['Health Status'],
        summary="Delete a health status",
        description="Delete an existing health status record by status_id.",
        responses={204: None},
    ),
)
class HealthStatusViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Health Status records. Consumed by the external Faculty System.
    Supports complete CRUD operations:
    - GET /api/health-statuses/ : List all health statuses
    - POST /api/health-statuses/ : Create a health status
    - GET /api/health-statuses/<status_id>/ : Retrieve a single status
    - PUT /api/health-statuses/<status_id>/ : Fully update a status
    - PATCH /api/health-statuses/<status_id>/ : Partially update a status
    - DELETE /api/health-statuses/<status_id>/ : Delete a status
    """
    queryset = HealthStatus.objects.select_related('student').all()
    serializer_class = HealthStatusSerializer
    lookup_field = 'status_id'
