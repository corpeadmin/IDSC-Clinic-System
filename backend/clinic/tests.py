"""
Comprehensive unit and integration test suite for IDSC Clinic System.
Tests models, serializers, API endpoints, relationships, validation constraints,
auto-incrementing primary keys, security, and error handling.
"""

from datetime import date, timedelta
from decimal import Decimal
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase
from clinic.models import Student, HealthRecord, SexChoices, BloodTypeChoices


class StudentModelTests(APITestCase):
    """Unit tests for the Student database model with auto-incrementing primary key."""

    def setUp(self):
        self.student = Student.objects.create(
            first_name="Juan",
            last_name="Dela Cruz",
            birth_date=date(2002, 5, 15),
            sex=SexChoices.MALE,
            course="BS Information Technology",
            section="3A",
            contact_no="09123456789"
        )

    def test_student_creation_and_auto_id(self):
        """Verify that student_id is auto-generated as an integer."""
        self.assertIsInstance(self.student.student_id, int)
        self.assertGreater(self.student.student_id, 0)
        self.assertEqual(self.student.first_name, "Juan")
        self.assertEqual(self.student.last_name, "Dela Cruz")
        self.assertEqual(self.student.full_name, "Juan Dela Cruz")
        self.assertEqual(str(self.student), f"{self.student.student_id} - Juan Dela Cruz")
        self.assertEqual(self.student.course, "BS Information Technology")
        self.assertEqual(self.student.section, "3A")
        self.assertEqual(self.student.contact_no, "09123456789")
        self.assertIsNotNone(self.student.created_at)
        self.assertIsNotNone(self.student.updated_at)

    def test_student_auto_increment(self):
        """Verify that sequential students receive auto-incrementing integer IDs."""
        student2 = Student.objects.create(
            first_name="Maria",
            last_name="Clara",
            course="BS Nursing",
            section="1A"
        )
        self.assertEqual(student2.student_id, self.student.student_id + 1)


class HealthRecordModelTests(APITestCase):
    """Unit tests for the HealthRecord database model and relationships."""

    def setUp(self):
        self.student = Student.objects.create(
            first_name="Maria",
            last_name="Santos",
            birth_date=date(2003, 8, 20),
            sex=SexChoices.FEMALE,
            course="BS Nursing",
            section="2B",
            contact_no="09987654321"
        )
        self.record = HealthRecord.objects.create(
            student=self.student,
            allergies="Penicillin, Dust",
            blood_type=BloodTypeChoices.O_POSITIVE,
            medical_history="Asthma diagnosed in 2015",
            medication="Salbutamol inhaler",
            weight=Decimal("52.50"),
            height=Decimal("160.00"),
            visit=timezone.now(),
            consultation="Routine checkup and asthma follow-up."
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
            first_name="Alice",
            last_name="Guinobatan",
            birth_date=date(2001, 1, 10),
            sex=SexChoices.FEMALE,
            course="BS Computer Science",
            section="4A",
            contact_no="09111111111"
        )
        self.student2 = Student.objects.create(
            first_name="Bob",
            last_name="Reyes",
            birth_date=date(2002, 2, 20),
            sex=SexChoices.MALE,
            course="BS Information Technology",
            section="3B",
            contact_no="09222222222"
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
        """GET /api/students/?search=... and ?course=... filter correctly."""
        # Search by name
        response = self.client.get('/api/students/?search=Alice')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['student_id'], self.student1.student_id)

        # Search by numeric student_id
        response = self.client.get(f'/api/students/?search={self.student1.student_id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['student_id'], self.student1.student_id)

        # Filter by course
        response = self.client.get('/api/students/?course=BS Computer Science')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['student_id'], self.student1.student_id)

    def test_create_student_success_auto_generated_id(self):
        """POST /api/students/ without student_id generates auto-incremented student_id."""
        payload = {
            "first_name": "Carlos",
            "last_name": "Mendoza",
            "birth_date": "2003-03-30",
            "sex": "Male",
            "course": "BS Nursing",
            "section": "1C",
            "contact_no": "09333333333"
        }
        response = self.client.post('/api/students/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('student_id', response.data)
        self.assertIsInstance(response.data['student_id'], int)
        self.assertEqual(response.data['first_name'], "Carlos")
        self.assertTrue(Student.objects.filter(pk=response.data['student_id']).exists())

    def test_create_student_ignores_client_provided_student_id(self):
        """POST /api/students/ ignores client-provided student_id and uses database auto-increment."""
        payload = {
            "student_id": 999999,  # Should be ignored (read-only)
            "first_name": "Diana",
            "last_name": "Prince",
            "course": "BSIT",
            "section": "2A"
        }
        response = self.client.post('/api/students/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Verify student_id was generated sequentially, not set to 999999
        self.assertNotEqual(response.data['student_id'], 999999)
        self.assertTrue(Student.objects.filter(pk=response.data['student_id']).exists())

    def test_create_student_future_birth_date_fails(self):
        """POST /api/students/ with future birth_date returns 400 Bad Request."""
        future_date = (date.today() + timedelta(days=10)).strftime('%Y-%m-%d')
        payload = {
            "first_name": "Future",
            "last_name": "Baby",
            "birth_date": future_date,
            "course": "BSIT",
            "section": "1A"
        }
        response = self.client.post('/api/students/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('birth_date', str(response.data))

    def test_get_single_student(self):
        """GET /api/students/<student_id>/ retrieves single student."""
        response = self.client.get(f'/api/students/{self.student1.student_id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['student_id'], self.student1.student_id)
        self.assertEqual(response.data['first_name'], "Alice")

    def test_get_nonexistent_student_returns_404(self):
        """GET /api/students/<student_id>/ with non-existent ID returns 404."""
        response = self.client.get('/api/students/999999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_put_update_student(self):
        """PUT /api/students/<student_id>/ fully updates student record."""
        payload = {
            "first_name": "Alicia",
            "last_name": "Guinobatan",
            "birth_date": "2001-01-10",
            "sex": "Female",
            "course": "BS Data Science",
            "section": "4B",
            "contact_no": "09119999999"
        }
        response = self.client.put(f'/api/students/{self.student1.student_id}/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], "Alicia")
        self.assertEqual(response.data['course'], "BS Data Science")
        
        self.student1.refresh_from_db()
        self.assertEqual(self.student1.first_name, "Alicia")
        self.assertEqual(self.student1.course, "BS Data Science")

    def test_patch_update_student(self):
        """PATCH /api/students/<student_id>/ partially updates student record."""
        payload = {"section": "4-Special"}
        response = self.client.patch(f'/api/students/{self.student1.student_id}/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['section'], "4-Special")
        self.assertEqual(response.data['first_name'], "Alice")

        self.student1.refresh_from_db()
        self.assertEqual(self.student1.section, "4-Special")

    def test_delete_student(self):
        """DELETE /api/students/<student_id>/ removes student (204 No Content)."""
        response = self.client.delete(f'/api/students/{self.student1.student_id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Student.objects.filter(pk=self.student1.student_id).exists())


class HealthRecordAPITests(APITestCase):
    """Integration tests for Health Record CRUD API endpoints."""

    def setUp(self):
        self.student = Student.objects.create(
            first_name="David",
            last_name="Tan",
            birth_date=date(2000, 11, 5),
            sex=SexChoices.MALE,
            course="BS Biology",
            section="4C",
            contact_no="09444444444"
        )
        self.record1 = HealthRecord.objects.create(
            student=self.student,
            allergies="Seafood",
            blood_type=BloodTypeChoices.A_POSITIVE,
            medical_history="None",
            medication="Antihistamine PRN",
            weight=Decimal("65.00"),
            height=Decimal("172.50"),
            visit=timezone.now() - timedelta(days=5),
            consultation="Allergic reaction to shrimp."
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
            "visit": timezone.now().isoformat(),
            "consultation": "Fever consultation, given paracetamol."
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
            "consultation": "Follow-up consultation after recovery."
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


class StudentHealthRecordRelationshipEndpointTests(APITestCase):
    """Integration tests for /api/students/<student_id>/health-records/ relationship endpoints."""

    def setUp(self):
        self.student = Student.objects.create(
            first_name="Elena",
            last_name="Ramos",
            birth_date=date(2004, 4, 12),
            sex=SexChoices.FEMALE,
            course="BS Pharmacy",
            section="2A",
            contact_no="09555555555"
        )
        self.other_student = Student.objects.create(
            first_name="Frank",
            last_name="Lim",
            course="BSIT",
            section="1A"
        )
        # Create 2 records for Elena
        self.record1 = HealthRecord.objects.create(
            student=self.student,
            allergies="Pollen",
            blood_type=BloodTypeChoices.B_POSITIVE,
            visit=timezone.now() - timedelta(days=2),
            consultation="First visit for rhinitis."
        )
        self.record2 = HealthRecord.objects.create(
            student=self.student,
            allergies="Pollen",
            blood_type=BloodTypeChoices.B_POSITIVE,
            visit=timezone.now(),
            consultation="Second visit for follow up."
        )
        # Create 1 record for Frank
        self.record_frank = HealthRecord.objects.create(
            student=self.other_student,
            blood_type=BloodTypeChoices.O_NEGATIVE,
            consultation="Annual physical exam."
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
            "consultation": "Created via nested relationship endpoint."
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


class ErrorHandlingAndValidationTests(APITestCase):
    """Tests for error handling, validation constraints, and security."""

    def test_student_blank_name_fails_validation(self):
        """Creating student with empty first_name or last_name returns 400."""
        payload = {
            "first_name": "   ",
            "last_name": "Test",
            "course": "BSIT",
            "section": "1A"
        }
        response = self.client.post('/api/students/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_student_invalid_sex_fails_validation(self):
        """Creating student with invalid sex choice returns 400."""
        payload = {
            "first_name": "Test",
            "last_name": "User",
            "sex": "InvalidSex",
            "course": "BSIT",
            "section": "1A"
        }
        response = self.client.post('/api/students/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_health_record_invalid_blood_type_fails_validation(self):
        """Creating health record with invalid blood type returns 400."""
        student = Student.objects.create(
            first_name="Test",
            last_name="User",
            course="BSIT",
            section="1A"
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
            first_name="Test",
            last_name="User",
            course="BSIT",
            section="1A"
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
