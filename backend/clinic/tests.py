"""
Comprehensive unit and integration test suite for IDSC Clinic System.
Tests models, serializers, API endpoints, relationships, validation constraints,
externally supplied primary keys, security, and error handling.
"""

from datetime import timedelta
from decimal import Decimal
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase
from clinic.models import Student, HealthRecord, Consultation, HealthStatus, BloodTypeChoices


class StudentModelTests(APITestCase):
    """Unit tests for the Student database model with externally supplied primary key."""

    def setUp(self):
        self.student = Student.objects.create(
            student_id=2026000001
        )

    def test_student_creation_with_external_id(self):
        """Verify that student_id is stored exactly as provided externally."""
        self.assertIsInstance(self.student.student_id, int)
        self.assertEqual(self.student.student_id, 2026000001)
        self.assertIsNotNone(self.student.created_at)
        self.assertIsNotNone(self.student.updated_at)

    def test_student_str_representation(self):
        """Verify string representation uses student_id."""
        self.assertEqual(str(self.student), "2026000001")


class HealthRecordModelTests(APITestCase):
    """Unit tests for the HealthRecord database model and relationships."""

    def setUp(self):
        self.student = Student.objects.create(
            student_id=2026000002
        )
        self.record = HealthRecord.objects.create(
            student=self.student,
            allergies="Penicillin, Dust",
            blood_type=BloodTypeChoices.O_POSITIVE,
            medical_history="Asthma diagnosed in 2015",
            medication="Salbutamol inhaler",
            weight=Decimal("52.50"),
            height=Decimal("160.00"),
        )

    def test_health_record_creation_and_relationship(self):
        """Verify health record creation and FK relationship with Student."""
        self.assertEqual(self.record.student, self.student)
        self.assertEqual(self.record.student_id, self.student.student_id)
        self.assertEqual(self.record.blood_type, BloodTypeChoices.O_POSITIVE)
        self.assertEqual(self.record.weight, Decimal("52.50"))
        self.assertEqual(self.record.height, Decimal("160.00"))
        self.assertEqual(self.student.health_records.count(), 1)
        self.assertEqual(self.student.health_records.first(), self.record)

    def test_cascade_delete_student_deletes_records(self):
        """Verify ON DELETE CASCADE removes associated health records when student is deleted."""
        record_id = self.record.health_id
        self.student.delete()
        self.assertFalse(HealthRecord.objects.filter(health_id=record_id).exists())


class StudentAPITests(APITestCase):
    """Integration tests for Student CRUD API endpoints."""

    def setUp(self):
        self.student1 = Student.objects.create(
            student_id=2026000003
        )
        self.student2 = Student.objects.create(
            student_id=2026000004
        )

    def test_get_all_students(self):
        """GET /api/students/ returns list of all students."""
        response = self.client.get('/api/students/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        student_ids = [s['student_id'] for s in response.data]
        self.assertIn(self.student1.student_id, student_ids)
        self.assertIn(self.student2.student_id, student_ids)

    def test_search_and_filter_students(self):
        """GET /api/students/?search=... filters correctly by student_id."""
        response = self.client.get(f'/api/students/?search={self.student1.student_id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['student_id'], self.student1.student_id)

    def test_create_student_success_with_external_id(self):
        """POST /api/students/ accepts externally supplied student_id."""
        payload = {
            "student_id": 2026000005
        }
        response = self.client.post('/api/students/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['student_id'], 2026000005)
        self.assertTrue(Student.objects.filter(pk=2026000005).exists())

    def test_get_single_student(self):
        """GET /api/students/<student_id>/ retrieves single student."""
        response = self.client.get(f'/api/students/{self.student1.student_id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['student_id'], self.student1.student_id)

    def test_get_nonexistent_student_returns_404(self):
        """GET /api/students/<student_id>/ with non-existent ID returns 404."""
        response = self.client.get('/api/students/999999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_put_update_student(self):
        """PUT /api/students/<student_id/> fully updates student record."""
        payload = {
            "student_id": self.student1.student_id
        }
        response = self.client.put(f'/api/students/{self.student1.student_id}/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['student_id'], self.student1.student_id)

    def test_patch_update_student(self):
        """PATCH /api/students/<student_id/> partially updates student record."""
        payload = {"student_id": self.student1.student_id}
        response = self.client.patch(f'/api/students/{self.student1.student_id}/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['student_id'], self.student1.student_id)

    def test_delete_student(self):
        """DELETE /api/students/<student_id/> removes student (204 No Content)."""
        response = self.client.delete(f'/api/students/{self.student1.student_id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Student.objects.filter(pk=self.student1.student_id).exists())


class HealthRecordAPITests(APITestCase):
    """Integration tests for Health Record CRUD API endpoints."""

    def setUp(self):
        self.student = Student.objects.create(
            student_id=2026000006
        )
        self.record1 = HealthRecord.objects.create(
            student=self.student,
            allergies="Seafood",
            blood_type=BloodTypeChoices.A_POSITIVE,
            medical_history="None",
            medication="Antihistamine PRN",
            weight=Decimal("65.00"),
            height=Decimal("172.50"),
        )

    def test_get_all_health_records(self):
        """GET /api/health-records/ returns list of health records."""
        response = self.client.get('/api/health-records/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['student_id'], self.student.student_id)

    def test_create_health_record_success(self):
        """POST /api/health-records/ creates a new health record with integer student_id."""
        payload = {
            "student_id": self.student.student_id,
            "allergies": "Aspirin",
            "blood_type": "A+",
            "medical_history": "Mild fever",
            "medication": "Paracetamol 500mg",
            "weight": "64.80",
            "height": "172.50",
        }
        response = self.client.post('/api/health-records/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['student_id'], self.student.student_id)
        self.assertEqual(response.data['blood_type'], "A+")
        self.assertEqual(HealthRecord.objects.count(), 2)

    def test_create_health_record_invalid_student_fails(self):
        """POST /api/health-records/ with invalid student_id returns 400 Bad Request."""
        payload = {
            "student_id": 999999,
            "allergies": "None",
            "blood_type": "O+"
        }
        response = self.client.post('/api/health-records/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('student_id', str(response.data))

    def test_create_health_record_invalid_weight_fails(self):
        """POST /api/health-records/ with negative weight returns 400 Bad Request."""
        payload = {
            "student_id": self.student.student_id,
            "weight": "-10.00"
        }
        response = self.client.post('/api/health-records/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('weight', str(response.data))

    def test_get_single_health_record(self):
        """GET /api/health-records/<health_id>/ retrieves record."""
        response = self.client.get(f'/api/health-records/{self.record1.health_id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['health_id'], self.record1.health_id)
        self.assertEqual(response.data['student_id'], self.student.student_id)

    def test_put_update_health_record(self):
        """PUT /api/health-records/<health_id>/ fully updates record."""
        payload = {
            "student_id": self.student.student_id,
            "allergies": "Seafood, Shellfish",
            "blood_type": "A+",
            "medical_history": "Asthma",
            "medication": "Cetirizine 10mg",
            "weight": "66.00",
            "height": "173.00",
        }
        response = self.client.put(f'/api/health-records/{self.record1.health_id}/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.record1.refresh_from_db()
        self.assertEqual(self.record1.allergies, "Seafood, Shellfish")
        self.assertEqual(self.record1.medication, "Cetirizine 10mg")

    def test_patch_update_health_record(self):
        """PATCH /api/health-records/<health_id>/ partially updates record."""
        payload = {"weight": "67.50"}
        response = self.client.patch(f'/api/health-records/{self.record1.health_id}/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.record1.refresh_from_db()
        self.assertEqual(self.record1.weight, Decimal("67.50"))

    def test_delete_health_record(self):
        """DELETE /api/health-records/<health_id>/ deletes record (204 No Content)."""
        response = self.client.delete(f'/api/health-records/{self.record1.health_id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(HealthRecord.objects.filter(health_id=self.record1.health_id).exists())


class ConsultationModelTests(APITestCase):
    """Unit tests for the Consultation database model and relationships."""

    def setUp(self):
        self.student = Student.objects.create(
            student_id=2026000016
        )
        self.consultation = Consultation.objects.create(
            student=self.student,
            consultation="Routine checkup and asthma follow-up.",
            visits=timezone.now()
        )

    def test_consultation_creation_and_relationship(self):
        """Verify consultation creation and FK relationship with Student."""
        self.assertEqual(self.consultation.student, self.student)
        self.assertEqual(self.consultation.student_id, self.student.student_id)
        self.assertEqual(self.consultation.consultation, "Routine checkup and asthma follow-up.")
        self.assertIsNotNone(self.consultation.visits)
        self.assertEqual(self.student.consultations.count(), 1)
        self.assertEqual(self.student.consultations.first(), self.consultation)

    def test_cascade_delete_student_deletes_consultations(self):
        """Verify ON DELETE CASCADE removes associated consultations when student is deleted."""
        consultation_id = self.consultation.consultation_id
        self.student.delete()
        self.assertFalse(Consultation.objects.filter(consultation_id=consultation_id).exists())


class ConsultationAPITests(APITestCase):
    """Integration tests for Consultation CRUD API endpoints."""

    def setUp(self):
        self.student = Student.objects.create(
            student_id=2026000017
        )
        self.consultation1 = Consultation.objects.create(
            student=self.student,
            consultation="Allergic reaction to shrimp.",
            visits=timezone.now() - timedelta(days=2)
        )

    def test_get_all_consultations(self):
        """GET /api/consultations/ returns list of consultations."""
        response = self.client.get('/api/consultations/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['student_id'], self.student.student_id)

    def test_create_consultation_success(self):
        """POST /api/consultations/ creates a new consultation with integer student_id."""
        payload = {
            "student_id": self.student.student_id,
            "consultation": "Fever consultation, given paracetamol.",
            "visits": timezone.now().isoformat()
        }
        response = self.client.post('/api/consultations/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['student_id'], self.student.student_id)
        self.assertEqual(response.data['consultation'], "Fever consultation, given paracetamol.")
        self.assertEqual(Consultation.objects.count(), 2)

    def test_create_consultation_invalid_student_fails(self):
        """POST /api/consultations/ with invalid student_id returns 400 Bad Request."""
        payload = {
            "student_id": 999999,
            "consultation": "Unwell"
        }
        response = self.client.post('/api/consultations/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('student_id', str(response.data))

    def test_get_single_consultation(self):
        """GET /api/consultations/<consultation_id>/ retrieves consultation."""
        response = self.client.get(f'/api/consultations/{self.consultation1.consultation_id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['consultation_id'], self.consultation1.consultation_id)
        self.assertEqual(response.data['student_id'], self.student.student_id)

    def test_put_update_consultation(self):
        """PUT /api/consultations/<consultation_id>/ fully updates consultation."""
        payload = {
            "student_id": self.student.student_id,
            "consultation": "Follow-up consultation after recovery.",
            "visits": timezone.now().isoformat()
        }
        response = self.client.put(f'/api/consultations/{self.consultation1.consultation_id}/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.consultation1.refresh_from_db()
        self.assertEqual(self.consultation1.consultation, "Follow-up consultation after recovery.")

    def test_patch_update_consultation(self):
        """PATCH /api/consultations/<consultation_id>/ partially updates consultation."""
        payload = {"consultation": "Improved notes"}
        response = self.client.patch(f'/api/consultations/{self.consultation1.consultation_id}/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.consultation1.refresh_from_db()
        self.assertEqual(self.consultation1.consultation, "Improved notes")

    def test_delete_consultation(self):
        """DELETE /api/consultations/<consultation_id>/ deletes consultation (204 No Content)."""
        response = self.client.delete(f'/api/consultations/{self.consultation1.consultation_id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Consultation.objects.filter(consultation_id=self.consultation1.consultation_id).exists())


class StudentConsultationRelationshipEndpointTests(APITestCase):
    """Integration tests for /api/students/<student_id>/consultations/ relationship endpoints."""

    def setUp(self):
        self.student = Student.objects.create(
            student_id=2026000018
        )
        self.other_student = Student.objects.create(
            student_id=2026000019
        )
        # Create 2 consultations for the student
        self.consultation1 = Consultation.objects.create(
            student=self.student,
            consultation="First visit for rhinitis.",
            visits=timezone.now() - timedelta(days=2)
        )
        self.consultation2 = Consultation.objects.create(
            student=self.student,
            consultation="Second visit for follow up.",
            visits=timezone.now()
        )
        # Create 1 consultation for the other student
        self.consultation_other = Consultation.objects.create(
            student=self.other_student,
            consultation="Annual physical exam."
        )

    def test_get_student_consultations(self):
        """GET /api/students/<student_id>/consultations/ returns only that student's consultations."""
        response = self.client.get(f'/api/students/{self.student.student_id}/consultations/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        for item in response.data:
            self.assertEqual(item['student_id'], self.student.student_id)

    def test_get_consultations_for_nonexistent_student_returns_404(self):
        """GET /api/students/<student_id>/consultations/ for non-existent student returns 404."""
        response = self.client.get('/api/students/999999/consultations/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_post_student_consultation_via_relationship(self):
        """POST /api/students/<student_id>/consultations/ creates consultation linked to student."""
        payload = {
            "consultation": "Created via nested relationship endpoint.",
            "visits": timezone.now().isoformat()
        }
        response = self.client.post(f'/api/students/{self.student.student_id}/consultations/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['student_id'], self.student.student_id)
        self.assertEqual(self.student.consultations.count(), 3)

    def test_post_student_consultation_for_nonexistent_student_returns_404(self):
        """POST /api/students/<student_id>/consultations/ for non-existent student returns 404."""
        payload = {
            "consultation": "Unwell"
        }
        response = self.client.post('/api/students/999999/consultations/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class StudentHealthRecordRelationshipEndpointTests(APITestCase):
    """Integration tests for /api/students/<student_id>/health-records/ relationship endpoints."""

    def setUp(self):
        self.student = Student.objects.create(
            student_id=2026000007
        )
        self.other_student = Student.objects.create(
            student_id=2026000008
        )
        # Create 2 records for Elena
        self.record1 = HealthRecord.objects.create(
            student=self.student,
            allergies="Pollen",
            blood_type=BloodTypeChoices.B_POSITIVE,
        )
        self.record2 = HealthRecord.objects.create(
            student=self.student,
            allergies="Pollen",
            blood_type=BloodTypeChoices.B_POSITIVE,
        )
        # Create 1 record for Frank
        self.record_frank = HealthRecord.objects.create(
            student=self.other_student,
            blood_type=BloodTypeChoices.O_NEGATIVE,
        )

    def test_get_student_health_records(self):
        """GET /api/students/<student_id>/health-records/ returns only that student's records."""
        response = self.client.get(f'/api/students/{self.student.student_id}/health-records/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        for item in response.data:
            self.assertEqual(item['student_id'], self.student.student_id)

    def test_get_health_records_for_nonexistent_student_returns_404(self):
        """GET /api/students/<student_id>/health-records/ for non-existent student returns 404."""
        response = self.client.get('/api/students/999999/health-records/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_post_student_health_record_via_relationship(self):
        """POST /api/students/<student_id>/health-records/ creates record linked to student."""
        payload = {
            "allergies": "Latex",
            "blood_type": "B+",
            "weight": "55.00",
            "height": "165.00",
        }
        response = self.client.post(f'/api/students/{self.student.student_id}/health-records/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['student_id'], self.student.student_id)
        self.assertEqual(self.student.health_records.count(), 3)

    def test_post_student_health_record_for_nonexistent_student_returns_404(self):
        """POST /api/students/<student_id>/health-records/ for non-existent student returns 404."""
        payload = {
            "allergies": "Latex",
            "blood_type": "B+",
            "weight": "55.00",
            "height": "165.00"
        }
        response = self.client.post('/api/students/999999/health-records/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class StudentPortalHealthRecordAPITests(APITestCase):
    """Integration tests for the view-only Student Portal health record endpoints."""

    def setUp(self):
        self.student1 = Student.objects.create(
            student_id=2026000012
        )
        self.student2 = Student.objects.create(
            student_id=2026000013
        )
        self.record1 = HealthRecord.objects.create(
            student=self.student1,
            allergies="Pollen",
            blood_type=BloodTypeChoices.B_POSITIVE,
        )
        self.record2 = HealthRecord.objects.create(
            student=self.student1,
            allergies="Pollen",
            blood_type=BloodTypeChoices.B_POSITIVE,
        )
        self.record3 = HealthRecord.objects.create(
            student=self.student2,
            blood_type=BloodTypeChoices.O_NEGATIVE,
        )

    def test_get_all_health_records(self):
        """GET /api/student-portal/health-records/ returns all health records."""
        response = self.client.get('/api/student-portal/health-records/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

    def test_get_students_health_records(self):
        """GET /api/student-portal/health-records/<student_id>/ returns only that student's records."""
        response = self.client.get(f'/api/student-portal/health-records/{self.student1.student_id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        for item in response.data:
            self.assertEqual(item['student_id'], self.student1.student_id)

    def test_get_health_records_for_nonexistent_student_returns_404(self):
        """GET /api/student-portal/health-records/<student_id>/ for non-existent student returns 404."""
        response = self.client.get('/api/student-portal/health-records/999999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_post_not_allowed(self):
        """POST /api/student-portal/health-records/ returns 405 (view-only API)."""
        response = self.client.post('/api/student-portal/health-records/', {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class HealthStatusModelTests(APITestCase):
    """Unit tests for the HealthStatus database model and relationships."""

    def setUp(self):
        self.student = Student.objects.create(
            student_id=2026000014
        )
        self.status = HealthStatus.objects.create(
            student=self.student,
            health_status="Healthy",
            date=timezone.now()
        )

    def test_health_status_creation_and_relationship(self):
        """Verify health status creation and FK relationship with Student."""
        self.assertEqual(self.status.student, self.student)
        self.assertEqual(self.status.student_id, self.student.student_id)
        self.assertEqual(self.status.health_status, "Healthy")
        self.assertEqual(self.student.health_statuses.count(), 1)

    def test_cascade_delete_student_deletes_statuses(self):
        """Verify ON DELETE CASCADE removes associated health statuses when student is deleted."""
        status_id = self.status.status_id
        self.student.delete()
        self.assertFalse(HealthStatus.objects.filter(status_id=status_id).exists())


class HealthStatusAPITests(APITestCase):
    """Integration tests for Health Status CRUD API endpoints."""

    def setUp(self):
        self.student = Student.objects.create(
            student_id=2026000015
        )
        self.status1 = HealthStatus.objects.create(
            student=self.student,
            health_status="Stable",
            date=timezone.now()
        )

    def test_get_all_health_statuses(self):
        """GET /api/health-statuses/ returns list of health statuses."""
        response = self.client.get('/api/health-statuses/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['student_id'], self.student.student_id)

    def test_create_health_status_success(self):
        """POST /api/health-statuses/ creates a new health status with integer student_id."""
        payload = {
            "student_id": self.student.student_id,
            "health_status": "Has cold",
            "date": timezone.now().isoformat()
        }
        response = self.client.post('/api/health-statuses/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['student_id'], self.student.student_id)
        self.assertEqual(response.data['health_status'], "Has cold")
        self.assertEqual(HealthStatus.objects.count(), 2)

    def test_create_health_status_invalid_student_fails(self):
        """POST /api/health-statuses/ with invalid student_id returns 400 Bad Request."""
        payload = {
            "student_id": 999999,
            "health_status": "Unwell"
        }
        response = self.client.post('/api/health-statuses/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('student_id', str(response.data))

    def test_get_single_health_status(self):
        """GET /api/health-statuses/<status_id>/ retrieves status."""
        response = self.client.get(f'/api/health-statuses/{self.status1.status_id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status_id'], self.status1.status_id)
        self.assertEqual(response.data['student_id'], self.student.student_id)

    def test_put_update_health_status(self):
        """PUT /api/health-statuses/<status_id>/ fully updates status."""
        payload = {
            "student_id": self.student.student_id,
            "health_status": "Recovered",
            "date": timezone.now().isoformat()
        }
        response = self.client.put(f'/api/health-statuses/{self.status1.status_id}/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.status1.refresh_from_db()
        self.assertEqual(self.status1.health_status, "Recovered")

    def test_patch_update_health_status(self):
        """PATCH /api/health-statuses/<status_id>/ partially updates status."""
        payload = {"health_status": "Improved"}
        response = self.client.patch(f'/api/health-statuses/{self.status1.status_id}/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.status1.refresh_from_db()
        self.assertEqual(self.status1.health_status, "Improved")

    def test_delete_health_status(self):
        """DELETE /api/health-statuses/<status_id>/ deletes status (204 No Content)."""
        response = self.client.delete(f'/api/health-statuses/{self.status1.status_id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(HealthStatus.objects.filter(status_id=self.status1.status_id).exists())


class ErrorHandlingAndValidationTests(APITestCase):
    """Tests for error handling, validation constraints, and security."""

    def test_student_duplicate_id_fails(self):
        """Creating student with duplicate student_id returns 400."""
        Student.objects.create(student_id=2026000009)
        payload = {
            "student_id": 2026000009
        }
        response = self.client.post('/api/students/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_health_record_invalid_blood_type_fails(self):
        """Creating health record with invalid blood type returns 400."""
        student = Student.objects.create(
            student_id=2026000010
        )
        payload = {
            "student_id": student.student_id,
            "blood_type": "X_POSITIVE"
        }
        response = self.client.post('/api/health-records/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_health_record_excessive_weight_and_height_fails(self):
        """Creating health record with weight > 500kg or height > 300cm returns 400."""
        student = Student.objects.create(
            student_id=2026000011
        )
        payload = {
            "student_id": student.student_id,
            "weight": "999.00",
            "height": "400.00"
        }
        response = self.client.post('/api/health-records/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_api_root_endpoint(self):
        """GET / returns API discovery metadata."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['status'], 'healthy')
