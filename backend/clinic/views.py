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

from .models import Student, HealthRecord
from .serializers import (
    StudentSerializer,
    StudentDetailSerializer,
    HealthRecordSerializer,
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
