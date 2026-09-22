"""
Django Admin configuration for IDSC Clinic System.
Registers Student, HealthRecord, Consultation, and HealthStatus models
with rich list displays, filters, search, and inlines.
"""

from django.contrib import admin
from .models import Student, HealthRecord, Consultation, HealthStatus


class HealthRecordInline(admin.TabularInline):
    """Inline view of Health Records inside Student admin change page."""
    model = HealthRecord
    extra = 0
    fields = ('health_id', 'blood_type', 'weight', 'height', 'allergies')
    readonly_fields = ('health_id', 'created_at', 'updated_at')


class ConsultationInline(admin.TabularInline):
    """Inline view of Consultations inside Student admin change page."""
    model = Consultation
    extra = 0
    fields = ('consultation_id', 'visits', 'consultation')
    readonly_fields = ('consultation_id', 'created_at', 'updated_at')
    ordering = ('-visits',)


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    """Admin configuration for Student model."""
    list_display = (
        'student_id',
        'created_at',
        'updated_at',
    )
    search_fields = (
        'student_id',
    )
    ordering = ('student_id',)
    inlines = [HealthRecordInline, ConsultationInline]
    fieldsets = (
        ('Student Identity', {
            'fields': ('student_id',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('student_id', 'created_at', 'updated_at')


@admin.register(HealthRecord)
class HealthRecordAdmin(admin.ModelAdmin):
    """Admin configuration for HealthRecord model."""
    list_display = (
        'health_id',
        'student',
        'blood_type',
        'weight',
        'height',
        'created_at',
    )
    list_filter = (
        'blood_type',
    )
    search_fields = (
        'student__student_id',
        'blood_type',
        'allergies',
        'medication',
    )
    ordering = ('-health_id',)
    raw_id_fields = ('student',)
    fieldsets = (
        ('Student Reference', {
            'fields': ('student',)
        }),
        ('Vitals & Physical Stats', {
            'fields': ('weight', 'height', 'blood_type')
        }),
        ('Medical Information', {
            'fields': ('allergies', 'medical_history', 'medication')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Consultation)
class ConsultationAdmin(admin.ModelAdmin):
    """Admin configuration for Consultation model."""
    list_display = (
        'consultation_id',
        'student',
        'visits',
        'created_at',
    )
    list_filter = (
        'visits',
    )
    search_fields = (
        'student__student_id',
        'consultation',
    )
    ordering = ('-visits', '-consultation_id')
    raw_id_fields = ('student',)
    fieldsets = (
        ('Student Reference', {
            'fields': ('student',)
        }),
        ('Consultation Information', {
            'fields': ('visits', 'consultation')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('created_at', 'updated_at')


@admin.register(HealthStatus)
class HealthStatusAdmin(admin.ModelAdmin):
    """Admin configuration for HealthStatus model."""
    list_display = (
        'status_id',
        'student',
        'health_status',
        'date',
        'created_at',
    )
    list_filter = (
        'date',
    )
    search_fields = (
        'student__student_id',
        'health_status',
    )
    ordering = ('-date', '-status_id')
    raw_id_fields = ('student',)
    fieldsets = (
        ('Student Reference', {
            'fields': ('student',)
        }),
        ('Status Information', {
            'fields': ('health_status', 'date')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('created_at', 'updated_at')
