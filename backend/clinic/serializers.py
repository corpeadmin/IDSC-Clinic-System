"""
Django REST Framework serializers for Student and HealthRecord models.
Provides full input validation, relationship handling, and serialization.
"""

from datetime import date
from rest_framework import serializers
from .models import Student, HealthRecord, SexChoices, BloodTypeChoices


class HealthRecordSerializer(serializers.ModelSerializer):
    """
    Serializer for the HealthRecord model.
    Handles foreign-key relationship with Student via student_id.
    """
    # Accept and display student_id as the primary key of the related Student
    student_id = serializers.PrimaryKeyRelatedField(
        queryset=Student.objects.all(),
        source='student',
        help_text="The ID of the student associated with this health record"
    )
    # Read-only student summary for convenience
    student_name = serializers.CharField(
        source='student.full_name',
        read_only=True
    )

    class Meta:
        model = HealthRecord
        fields = [
            'health_id',
            'student_id',
            'student_name',
            'allergies',
            'blood_type',
            'medical_history',
            'medication',
            'weight',
            'height',
            'visit',
            'consultation',
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


class StudentSerializer(serializers.ModelSerializer):
    """
    Serializer for the Student model.
    Handles student CRUD with validation on unique student_id and fields.
    """
    health_records_count = serializers.IntegerField(
        source='health_records.count',
        read_only=True
    )

    class Meta:
        model = Student
        fields = [
            'student_id',
            'first_name',
            'last_name',
            'birth_date',
            'sex',
            'course',
            'section',
            'contact_no',
            'health_records_count',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['student_id', 'created_at', 'updated_at']

    def validate_first_name(self, value):
        cleaned = value.strip()
        if not cleaned:
            raise serializers.ValidationError("First name cannot be blank.")
        return cleaned

    def validate_last_name(self, value):
        cleaned = value.strip()
        if not cleaned:
            raise serializers.ValidationError("Last name cannot be blank.")
        return cleaned

    def validate_course(self, value):
        cleaned = value.strip()
        if not cleaned:
            raise serializers.ValidationError("Course cannot be blank.")
        return cleaned

    def validate_section(self, value):
        cleaned = value.strip()
        if not cleaned:
            raise serializers.ValidationError("Section cannot be blank.")
        return cleaned

    def validate_birth_date(self, value):
        """Validate birth date is not in the future."""
        if value and value > date.today():
            raise serializers.ValidationError("Birth date cannot be in the future.")
        return value

    def validate_sex(self, value):
        """Validate sex choice if provided."""
        if value and value not in SexChoices.values:
            valid_choices = ", ".join(SexChoices.values)
            raise serializers.ValidationError(f"Invalid sex value. Valid options are: {valid_choices}")
        return value


class StudentDetailSerializer(StudentSerializer):
    """
    Detailed Student Serializer including nested health records history.
    """
    health_records = HealthRecordSerializer(many=True, read_only=True)

    class Meta(StudentSerializer.Meta):
        fields = StudentSerializer.Meta.fields + ['health_records']
