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

from .models import Student, HealthRecord
from .serializers import (
    StudentSerializer,
    StudentDetailSerializer,
    HealthRecordSerializer,
)


@extend_schema_view(
    list=extend_schema(
        tags=['Students'],
        summary="List all students",
        description="Retrieve a list of all students with optional search and filtering by course, section, or sex.",
        parameters=[
            OpenApiParameter(
                name='search',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Search keyword matching first name, last name, course, section, or student ID'
            ),
            OpenApiParameter(
                name='course',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Filter by degree program / course (case-insensitive exact match)'
            ),
            OpenApiParameter(
                name='section',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Filter by section (case-insensitive exact match)'
            ),
            OpenApiParameter(
                name='sex',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                enum=['Male', 'Female', 'Other'],
                description="Filter by sex (Male, Female, Other)"
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
        description="Register a new student record in the IDSC Clinic System.",
        request=StudentSerializer,
        responses={201: StudentSerializer},
    ),
    update=extend_schema(
        tags=['Students'],
        summary="Update a student",
        description="Update all fields of an existing student record.",
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
                description='Search keyword matching student name, allergies, consultation notes, medical history, or student ID'
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
                Q(student__first_name__icontains=search) |
                Q(student__last_name__icontains=search) |
                Q(allergies__icontains=search) |
                Q(consultation__icontains=search) |
                Q(medical_history__icontains=search)
            )
            if search.isdigit():
                filters |= Q(student__student_id=int(search))
            queryset = queryset.filter(filters)

        return queryset
