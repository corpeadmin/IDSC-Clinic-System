"""
Django REST Framework serializers for Student and HealthRecord models.
Provides full input validation, relationship handling, and serialization.
"""

from datetime import date
from rest_framework import serializers
from .models import (
    Student,
    HealthRecord,
    Medicine,
    DispensingRecord,
    StockTransaction,
    SexChoices,
    BloodTypeChoices,
)


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


class MedicineSerializer(serializers.ModelSerializer):
    """
    Serializer for medicines in the clinic inventory.
    """

    is_low_stock = serializers.SerializerMethodField()

    class Meta:
        model = Medicine
        fields = [
            'medicine_id',
            'name',
            'generic_name',
            'unit',
            'quantity_in_stock',
            'reorder_level',
            'expiration_date',
            'is_active',
            'is_low_stock',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'medicine_id',
            'quantity_in_stock',
            'is_low_stock',
            'created_at',
            'updated_at',
        ]

    def get_is_low_stock(self, obj):
        return obj.quantity_in_stock <= obj.reorder_level

    def validate_name(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Medicine name cannot be blank."
            )

        return value

    def validate_unit(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Medicine unit cannot be blank."
            )

        return value

    def validate(self, attrs):
        reorder_level = attrs.get(
            'reorder_level',
            getattr(self.instance, 'reorder_level', 0)
        )

        if reorder_level < 0:
            raise serializers.ValidationError({
                'reorder_level': 'Reorder level cannot be negative.'
            })

        return attrs


class DispensingRecordSerializer(serializers.ModelSerializer):
    """
    Serializer for medicine dispensing records.
    """

    medicine_name = serializers.CharField(
        source='medicine.name',
        read_only=True
    )
    student_name = serializers.CharField(
        source='student.full_name',
        read_only=True
    )
    dispensed_by_username = serializers.CharField(
        source='dispensed_by.username',
        read_only=True
    )

    class Meta:
        model = DispensingRecord
        fields = [
            'dispensing_id',
            'medicine',
            'medicine_name',
            'student',
            'student_name',
            'quantity',
            'dispensed_by',
            'dispensed_by_username',
            'dispensed_at',
            'remarks',
        ]
        read_only_fields = [
            'dispensing_id',
            'dispensed_by',
            'dispensed_by_username',
            'dispensed_at',
        ]

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                "Dispensing quantity must be greater than 0."
            )

        return value

    def validate(self, attrs):
        medicine = attrs.get('medicine')

        if medicine and not medicine.is_active:
            raise serializers.ValidationError({
                'medicine': 'This medicine is inactive and cannot be dispensed.'
            })

        return attrs


class StockTransactionSerializer(serializers.ModelSerializer):
    """
    Serializer for medicine stock transaction history.
    """

    medicine_name = serializers.CharField(
        source='medicine.name',
        read_only=True
    )
    created_by_username = serializers.CharField(
        source='created_by.username',
        read_only=True
    )
    transaction_type_display = serializers.CharField(
        source='get_transaction_type_display',
        read_only=True
    )

    class Meta:
        model = StockTransaction
        fields = [
            'transaction_id',
            'medicine',
            'medicine_name',
            'transaction_type',
            'transaction_type_display',
            'quantity',
            'previous_stock',
            'new_stock',
            'created_by',
            'created_by_username',
            'created_at',
            'remarks',
        ]
        read_only_fields = [
            'transaction_id',
            'previous_stock',
            'new_stock',
            'created_by',
            'created_by_username',
            'created_at',
        ]

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                "Transaction quantity must be greater than 0."
            )

        return value


class StockInSerializer(serializers.Serializer):
    """
    Serializer for adding medicine stock.
    """

    quantity = serializers.IntegerField(min_value=1)

    remarks = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=500,
    )


class StockAdjustmentSerializer(serializers.Serializer):
    """
    Serializer for adjusting medicine stock.
    """

    quantity = serializers.IntegerField(min_value=1)

    adjustment = serializers.ChoiceField(
        choices=[
            ('INCREASE', 'Increase'),
            ('DECREASE', 'Decrease'),
        ]
    )

    remarks = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=500,
    )