"""
Database models for IDSC Clinic System.
Defines Student and HealthRecord entities with appropriate PostgreSQL-compatible types,
constraints, relationships, and indexes.
"""

from decimal import Decimal
from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator


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
    Uses externally supplied student_id as the primary identifier.
    """
    student_id = models.BigIntegerField(
        primary_key=True,
        help_text="Externally supplied unique student identifier"
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

    def __str__(self):
        return f"{self.student_id}"


class HealthRecord(models.Model):
    """
    HealthRecord model representing medical and physical information
    for a specific student. Clinic consultations and visit dates are
    tracked separately in the Consultation model.
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
        ordering = ['-health_id']
        verbose_name = 'Health Record'
        verbose_name_plural = 'Health Records'
        indexes = [
            models.Index(fields=['student', '-health_id'], name='idx_hr_student_id'),
        ]

    def __str__(self):
        return f"Record #{self.health_id} - Student: {self.student_id}"


class Consultation(models.Model):
    """
    Consultation model representing clinic consultation notes and the
    associated visit date/time for a specific student.
    """
    consultation_id = models.BigAutoField(
        primary_key=True,
        help_text="Unique consultation identifier"
    )
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='consultations',
        db_column='student_id',
        help_text="The student associated with this consultation"
    )
    consultation = models.TextField(
        blank=True,
        default='',
        help_text="Clinic consultation notes, diagnosis, and treatment provided"
    )
    visits = models.DateTimeField(
        default=timezone.now,
        help_text="Date and time of clinic visit"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when consultation was created"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when consultation was last updated"
    )

    class Meta:
        db_table = 'consultations'
        ordering = ['-visits', '-consultation_id']
        verbose_name = 'Consultation'
        verbose_name_plural = 'Consultations'
        indexes = [
            models.Index(fields=['student', '-visits'], name='idx_c_student_visit'),
            models.Index(fields=['-visits'], name='idx_c_visit'),
        ]

    def __str__(self):
        visit_str = self.visits.strftime('%Y-%m-%d %H:%M') if self.visits else 'N/A'
        return f"Consultation #{self.consultation_id} - Student: {self.student_id} ({visit_str})"


class HealthStatus(models.Model):
    """
    HealthStatus model representing the current health status reported for a specific student.
    Consumed via CRUD API by the external Faculty System.
    """
    status_id = models.BigAutoField(
        primary_key=True,
        help_text="Unique health status identifier"
    )
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='health_statuses',
        db_column='student_id',
        help_text="The student associated with this health status"
    )
    health_status = models.TextField(
        blank=True,
        default='',
        help_text="Health status details reported for the student"
    )
    date = models.DateTimeField(
        default=timezone.now,
        help_text="Date and time the health status was recorded"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when health status was created"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when health status was last updated"
    )

    class Meta:
        db_table = 'health_statuses'
        ordering = ['-date', '-status_id']
        verbose_name = 'Health Status'
        verbose_name_plural = 'Health Statuses'
        indexes = [
            models.Index(fields=['student', '-date'], name='idx_hs_student_date'),
            models.Index(fields=['-date'], name='idx_hs_date'),
        ]

    def __str__(self):
        date_str = self.date.strftime('%Y-%m-%d %H:%M') if self.date else 'N/A'
        return f"Status #{self.status_id} - Student: {self.student_id} ({date_str})"
