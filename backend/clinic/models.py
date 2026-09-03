"""
Database models for IDSC Clinic System.
Defines Student and HealthRecord entities with appropriate PostgreSQL-compatible types,
constraints, relationships, and indexes.
"""

from decimal import Decimal
from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator


class SexChoices(models.TextChoices):
    MALE = 'Male', 'Male'
    FEMALE = 'Female', 'Female'
    OTHER = 'Other', 'Other'


class BloodTypeChoices(models.TextChoices):
    A_POSITIVE = 'A+', 'A+'
    A_NEGATIVE = 'A-', 'A-'
    B_POSITIVE = 'B+', 'B+'
    B_NEGATIVE = 'B-', 'B-'
    AB_POSITIVE = 'AB+', 'AB+'
    AB_NEGATIVE = 'AB-', 'AB-'
    O_POSITIVE = 'O+', 'O+'
    O_NEGATIVE = 'O-', 'O-'
    UNKNOWN = 'Unknown', 'Unknown'


class Student(models.Model):
    """
    Student model representing enrolled students visiting the IDSC Clinic.
    Uses student_id as the primary identifier.
    """
    student_id = models.BigAutoField(
        primary_key=True,
        help_text="Auto-incrementing unique student identifier"
    )
    first_name = models.CharField(
        max_length=100,
        help_text="Student's first name"
    )
    last_name = models.CharField(
        max_length=100,
        help_text="Student's last name"
    )
    birth_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date of birth (YYYY-MM-DD)"
    )
    sex = models.CharField(
        max_length=20,
        choices=SexChoices.choices,
        blank=True,
        default='',
        help_text="Student's sex/gender"
    )
    course = models.CharField(
        max_length=100,
        help_text="Degree program or course (e.g. BSIT, BSCS, BSN)"
    )
    section = models.CharField(
        max_length=50,
        help_text="Class section (e.g. 3A, 1-1, CS401)"
    )
    contact_no = models.CharField(
        max_length=30,
        blank=True,
        default='',
        help_text="Contact number or mobile phone"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when student record was created"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when student record was last updated"
    )

    class Meta:
        db_table = 'students'
        ordering = ['student_id']
        verbose_name = 'Student'
        verbose_name_plural = 'Students'
        indexes = [
            models.Index(fields=['last_name', 'first_name'], name='idx_student_name'),
            models.Index(fields=['course', 'section'], name='idx_student_course_sec'),
        ]

    def __str__(self):
        return f"{self.student_id} - {self.first_name} {self.last_name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class HealthRecord(models.Model):
    """
    HealthRecord model representing clinic consultations, visits, and medical information
    for a specific student.
    """
    health_id = models.BigAutoField(
        primary_key=True,
        help_text="Unique health record identifier"
    )
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='health_records',
        db_column='student_id',
        help_text="The student associated with this health record"
    )
    allergies = models.TextField(
        blank=True,
        default='',
        help_text="Known allergies (e.g. penicillin, peanuts, pollen)"
    )
    blood_type = models.CharField(
        max_length=10,
        choices=BloodTypeChoices.choices,
        blank=True,
        default='',
        help_text="Blood type (e.g. A+, O+, etc.)"
    )
    medical_history = models.TextField(
        blank=True,
        default='',
        help_text="Past medical history and chronic conditions (e.g. Asthma, Hypertension)"
    )
    medication = models.TextField(
        blank=True,
        default='',
        help_text="Current medications and prescriptions"
    )
    weight = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0.0')), MaxValueValidator(Decimal('500.0'))],
        help_text="Weight in kilograms (kg)"
    )
    height = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0.0')), MaxValueValidator(Decimal('300.0'))],
        help_text="Height in centimeters (cm)"
    )
    visit = models.DateTimeField(
        default=timezone.now,
        help_text="Date and time of clinic visit"
    )
    consultation = models.TextField(
        blank=True,
        default='',
        help_text="Clinic consultation notes, diagnosis, and treatment provided"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when health record was created"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when health record was last updated"
    )

    class Meta:
        db_table = 'health_records'
        ordering = ['-visit', '-health_id']
        verbose_name = 'Health Record'
        verbose_name_plural = 'Health Records'
        indexes = [
            models.Index(fields=['student', '-visit'], name='idx_hr_student_visit'),
            models.Index(fields=['-visit'], name='idx_hr_visit'),
        ]

    def __str__(self):
        visit_str = self.visit.strftime('%Y-%m-%d %H:%M') if self.visit else 'N/A'
        return f"Record #{self.health_id} - Student: {self.student_id} ({visit_str})"

class Medicine(models.Model):
    """
    Medicine available in the clinic inventory.
    Tracks current stock and the minimum level before
    the medicine is considered low stock.
    """
    medicine_id = models.BigAutoField(
        primary_key=True,
        help_text="Unique medicine identifier"
    )
    name = models.CharField(
        max_length=150,
        help_text="Medicine name"
    )
    generic_name = models.CharField(
        max_length=150,
        blank=True,
        default='',
        help_text="Generic name of the medicine"
    )
    unit = models.CharField(
        max_length=50,
        help_text="Unit of measurement (e.g. tablet, capsule, bottle)"
    )
    quantity_in_stock = models.PositiveIntegerField(
        default=0,
        help_text="Current quantity available in stock"
    )
    reorder_level = models.PositiveIntegerField(
        default=10,
        help_text="Stock level at which medicine is considered low stock"
    )
    expiration_date = models.DateField(
        null=True,
        blank=True,
        help_text="Medicine expiration date"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this medicine is currently available for dispensing"
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        db_table = 'medicines'
        ordering = ['name']
        verbose_name = 'Medicine'
        verbose_name_plural = 'Medicines'
        indexes = [
            models.Index(
                fields=['name'],
                name='idx_medicine_name'
            ),
            models.Index(
                fields=['quantity_in_stock'],
                name='idx_medicine_stock'
            ),
        ]

    def __str__(self):
        return f"{self.name} ({self.quantity_in_stock} {self.unit})"


class DispensingRecord(models.Model):
    """
    Records medicine dispensed to a student.
    Each dispensing operation reduces the medicine stock.
    """
    dispensing_id = models.BigAutoField(
        primary_key=True,
        help_text="Unique dispensing record identifier"
    )
    medicine = models.ForeignKey(
        Medicine,
        on_delete=models.PROTECT,
        related_name='dispensing_records',
        db_column='medicine_id',
        help_text="Medicine that was dispensed"
    )
    student = models.ForeignKey(
        Student,
        on_delete=models.PROTECT,
        related_name='dispensing_records',
        db_column='student_id',
        help_text="Student who received the medicine"
    )
    quantity = models.PositiveIntegerField(
        help_text="Quantity of medicine dispensed"
    )
    dispensed_by = models.ForeignKey(
        'auth.User',
        on_delete=models.PROTECT,
        related_name='dispensing_records',
        help_text="User who dispensed the medicine"
    )
    dispensed_at = models.DateTimeField(
        default=timezone.now
    )
    remarks = models.TextField(
        blank=True,
        default='',
        help_text="Additional notes about the dispensing"
    )

    class Meta:
        db_table = 'dispensing_records'
        ordering = ['-dispensed_at', '-dispensing_id']
        indexes = [
            models.Index(
                fields=['student', '-dispensed_at'],
                name='idx_disp_student_date'
            ),
            models.Index(
                fields=['medicine', '-dispensed_at'],
                name='idx_disp_medicine_date'
            ),
        ]

    def __str__(self):
        return (
            f"Dispensing #{self.dispensing_id} - "
            f"{self.medicine.name} x{self.quantity}"
        )


class StockTransaction(models.Model):
    """
    Records every change made to medicine stock.
    Provides an audit trail for inventory changes.
    """

    class TransactionType(models.TextChoices):
        STOCK_IN = 'STOCK_IN', 'Stock In'
        DISPENSE = 'DISPENSE', 'Dispense'
        ADJUSTMENT = 'ADJUSTMENT', 'Adjustment'

    transaction_id = models.BigAutoField(
        primary_key=True,
        help_text="Unique stock transaction identifier"
    )
    medicine = models.ForeignKey(
        Medicine,
        on_delete=models.PROTECT,
        related_name='stock_transactions',
        db_column='medicine_id',
        help_text="Medicine affected by the transaction"
    )
    transaction_type = models.CharField(
        max_length=20,
        choices=TransactionType.choices,
        help_text="Type of stock transaction"
    )
    quantity = models.PositiveIntegerField(
        help_text="Quantity involved in the transaction"
    )
    previous_stock = models.PositiveIntegerField(
        help_text="Stock quantity before the transaction"
    )
    new_stock = models.PositiveIntegerField(
        help_text="Stock quantity after the transaction"
    )
    created_by = models.ForeignKey(
        'auth.User',
        on_delete=models.PROTECT,
        related_name='stock_transactions',
        help_text="User who performed the transaction"
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )
    remarks = models.TextField(
        blank=True,
        default='',
        help_text="Additional notes about the transaction"
    )

    class Meta:
        db_table = 'stock_transactions'
        ordering = ['-created_at', '-transaction_id']
        indexes = [
            models.Index(
                fields=['medicine', '-created_at'],
                name='idx_stock_medicine_date'
            ),
            models.Index(
                fields=['transaction_type', '-created_at'],
                name='idx_stock_type_date'
            ),
        ]

    def __str__(self):
        return (
            f"{self.transaction_type} - "
            f"{self.medicine.name} ({self.quantity})"
        )
