"""
Django Admin configuration for IDSC Clinic System.
Registers Student and HealthRecord models with rich list displays, filters, search, and inlines.
"""

from django.contrib import admin
from .models import Student, HealthRecord


class HealthRecordInline(admin.TabularInline):
    """Inline view of Health Records inside Student admin change page."""
    model = HealthRecord
    extra = 0
    fields = ('health_id', 'visit', 'blood_type', 'weight', 'height', 'allergies', 'consultation')
    readonly_fields = ('health_id', 'created_at', 'updated_at')
    ordering = ('-visit',)


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    """Admin configuration for Student model."""
    list_display = (
        'student_id',
        'first_name',
        'last_name',
        'course',
        'section',
        'sex',
        'contact_no',
        'birth_date',
        'created_at',
    )
    list_filter = (
        'course',
        'section',
        'sex',
    )
    search_fields = (
        'student_id',
        'first_name',
        'last_name',
        'course',
        'section',
        'contact_no',
    )
    ordering = ('student_id',)
    inlines = [HealthRecordInline]
    fieldsets = (
        ('Student Identity', {
            'fields': ('student_id', 'first_name', 'last_name')
        }),
        ('Academic Details', {
            'fields': ('course', 'section')
        }),
        ('Personal & Contact Information', {
            'fields': ('birth_date', 'sex', 'contact_no')
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
        'visit',
        'weight',
        'height',
        'created_at',
    )
    list_filter = (
        'blood_type',
        'visit',
    )
    search_fields = (
        'student__student_id',
        'student__first_name',
        'student__last_name',
        'blood_type',
        'allergies',
        'medication',
        'consultation',
    )
    ordering = ('-visit', '-health_id')
    raw_id_fields = ('student',)
    fieldsets = (
        ('Student Reference', {
            'fields': ('student',)
        }),
        ('Visit Information', {
            'fields': ('visit',)
        }),
        ('Vitals & Physical Stats', {
            'fields': ('weight', 'height', 'blood_type')
        }),
        ('Medical Information', {
            'fields': ('allergies', 'medical_history', 'medication', 'consultation')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('created_at', 'updated_at')
