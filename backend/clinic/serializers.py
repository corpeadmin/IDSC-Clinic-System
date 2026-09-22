"""
Django REST Framework serializers for Student, HealthRecord, and Consultation models.
Provides full input validation, relationship handling, and serialization.
"""

from rest_framework import serializers
from .models import Student, HealthRecord, Consultation, HealthStatus, BloodTypeChoices


class HealthRecordSerializer(serializers.ModelSerializer):
    """
    Serializer for the HealthRecord model.
    Handles foreign-key relationship with Student via student_id.
    Clinic consultations and visit dates live in the separate Consultation model.
    """
    # Accept and display student_id as the primary key of the related Student
    student_id = serializers.PrimaryKeyRelatedField(
        queryset=Student.objects.all(),
        source='student',
        help_text="The ID of the student associated with this health record"
    )

    class Meta:
        model = HealthRecord
        fields = [
            'health_id',
            'student_id',
            'allergies',
            'blood_type',
            'medical_history',
            'medication',
            'weight',
            'height',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['health_id', 'created_at', 'updated_at']

    def validate_weight(self, value):
        """Validate weight value."""
        if value is not None and value <= 0:
            raise serializers.ValidationError("Weight must be greater than 0 kg.")
        if value is not None and value > 500:
            raise serializers.ValidationError("Weight cannot exceed 500 kg.")
        return value

    def validate_height(self, value):
        """Validate height value."""
        if value is not None and value <= 0:
            raise serializers.ValidationError("Height must be greater than 0 cm.")
        if value is not None and value > 300:
            raise serializers.ValidationError("Height cannot exceed 300 cm.")
        return value

    def validate_blood_type(self, value):
        """Validate blood type choice if provided."""
        if value and value not in BloodTypeChoices.values:
            valid_choices = ", ".join(BloodTypeChoices.values)
            raise serializers.ValidationError(f"Invalid blood type. Valid options are: {valid_choices}")
        return value


class ConsultationSerializer(serializers.ModelSerializer):
    """
    Serializer for the Consultation model.
    Handles foreign-key relationship with Student via student_id.
    """
    # Accept and display student_id as the primary key of the related Student
    student_id = serializers.PrimaryKeyRelatedField(
        queryset=Student.objects.all(),
        source='student',
        help_text="The ID of the student associated with this consultation"
    )

    class Meta:
        model = Consultation
        fields = [
            'consultation_id',
            'student_id',
            'consultation',
            'visits',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['consultation_id', 'created_at', 'updated_at']


class HealthStatusSerializer(serializers.ModelSerializer):
    """
    Serializer for the HealthStatus model.
    Handles foreign-key relationship with Student via student_id.
    """
    # Accept and display student_id as the primary key of the related Student
    student_id = serializers.PrimaryKeyRelatedField(
        queryset=Student.objects.all(),
        source='student',
        help_text="The ID of the student associated with this health status"
    )

    class Meta:
        model = HealthStatus
        fields = [
            'status_id',
            'student_id',
            'health_status',
            'date',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['status_id', 'created_at', 'updated_at']


class StudentSerializer(serializers.ModelSerializer):
    """
    Serializer for the Student model.
    Handles student CRUD with externally supplied student_id.
    """
    health_records_count = serializers.IntegerField(
        source='health_records.count',
        read_only=True
    )
    consultations_count = serializers.IntegerField(
        source='consultations.count',
        read_only=True
    )

    class Meta:
        model = Student
        fields = [
            'student_id',
            'health_records_count',
            'consultations_count',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['health_records_count', 'consultations_count', 'created_at', 'updated_at']


class StudentDetailSerializer(StudentSerializer):
    """
    Detailed Student Serializer including nested health records and consultation history.
    """
    health_records = HealthRecordSerializer(many=True, read_only=True)
    consultations = ConsultationSerializer(many=True, read_only=True)

    class Meta(StudentSerializer.Meta):
        fields = StudentSerializer.Meta.fields + ['health_records', 'consultations']
