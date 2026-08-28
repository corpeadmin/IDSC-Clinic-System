# IDSC Clinic System API Reference

Interactive API documentation and comprehensive reference for the IDSC Clinic System REST backend.

---

## Table of Contents

- [Overview](#overview)
- [Base URL](#base-url)
- [Interactive Documentation](#interactive-documentation)
- [Authentication & Permissions](#authentication--permissions)
- [Standard Response & Error Format](#standard-response--error-format)
- [Endpoints Summary](#endpoints-summary)
- [Students API](#students-api)
  - [1. List Students](#1-list-students)
  - [2. Create Student](#2-create-student)
  - [3. Retrieve Student Details](#3-retrieve-student-details)
  - [4. Fully Update Student](#4-fully-update-student)
  - [5. Partially Update Student](#5-partially-update-student)
  - [6. Delete Student](#6-delete-student)
  - [7. List Health Records for Student](#7-list-health-records-for-student)
  - [8. Create Health Record for Student](#8-create-health-record-for-student)
- [Health Records API](#health-records-api)
  - [1. List Health Records](#1-list-health-records)
  - [2. Create Health Record](#2-create-health-record)
  - [3. Retrieve Health Record](#3-retrieve-health-record)
  - [4. Fully Update Health Record](#4-fully-update-health-record)
  - [5. Partially Update Health Record](#5-partially-update-health-record)
  - [6. Delete Health Record](#6-delete-health-record)
- [System & Discovery Endpoints](#system--discovery-endpoints)

---

## Overview

The IDSC Clinic System API provides complete CRUD functionality for managing clinic operations, student patient profiles, and medical consultation records.

- **API Version:** `1.0.0`
- **Format:** JSON (`application/json`)
- **OpenAPI Version:** `3.0.3`

---

## Base URL

| Environment | Base URL |
| :--- | :--- |
| **Development** | `http://127.0.0.1:8000` or `http://localhost:8000` |
| **API Prefix** | `/api/` |

---

## Interactive Documentation

Interactive documentation interfaces and the raw OpenAPI 3.0 schema are served directly by the backend:

| Interface | URL Path | Description |
| :--- | :--- | :--- |
| **Swagger UI** | `/api/docs/` | Interactive API explorer to test requests directly in browser |
| **ReDoc** | `/api/redoc/` | Clean, responsive reference documentation |
| **OpenAPI Schema** | `/api/schema/` | Raw OpenAPI 3.0 YAML/JSON specification |

---

## Authentication & Permissions

- **Default Permission:** `AllowAny` (public access for clinic frontend client integration).
- **Supported Schemes:** Session Authentication (`cookieAuth` via `sessionid`), HTTP Basic Authentication (`basicAuth`).

---

## Standard Response & Error Format

All API errors return standardized JSON structures processed by the backend exception handler:

### Standard Error Response Format

```json
{
  "success": false,
  "status_code": 400,
  "errors": {
    "first_name": [
      "First name cannot be blank."
    ]
  }
}
```

### 404 Not Found Response

```json
{
  "success": false,
  "status_code": 404,
  "errors": {
    "detail": "The requested resource was not found."
  }
}
```

### 500 Internal Server Error Response

```json
{
  "success": false,
  "status_code": 500,
  "errors": {
    "detail": "An unexpected server error occurred."
  }
}
```

---

## Endpoints Summary

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/students/` | List all students with search and filtering |
| `POST` | `/api/students/` | Register a new student |
| `GET` | `/api/students/{student_id}/` | Retrieve student details and nested health records |
| `PUT` | `/api/students/{student_id}/` | Update all fields of a student |
| `PATCH` | `/api/students/{student_id}/` | Partially update fields of a student |
| `DELETE` | `/api/students/{student_id}/` | Delete student and all associated records |
| `GET` | `/api/students/{student_id}/health-records/` | List health records for a specific student |
| `POST` | `/api/students/{student_id}/health-records/` | Create health record for a specific student |
| `GET` | `/api/health-records/` | List all health records with filtering |
| `POST` | `/api/health-records/` | Create a new health record |
| `GET` | `/api/health-records/{health_id}/` | Retrieve details of a health record |
| `PUT` | `/api/health-records/{health_id}/` | Update all fields of a health record |
| `PATCH` | `/api/health-records/{health_id}/` | Partially update fields of a health record |
| `DELETE` | `/api/health-records/{health_id}/` | Delete a health record |
| `GET` | `/` | API discovery and health status endpoint |
| `GET` | `/api/schema/` | OpenAPI 3.0 schema file download |
| `GET` | `/api/docs/` | Swagger UI documentation |
| `GET` | `/api/redoc/` | ReDoc documentation |

---

## Students API

### 1. List Students

Retrieve a list of students with optional query parameter filtering.

- **HTTP Method:** `GET`
- **Path:** `/api/students/`

#### Query Parameters

| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `search` | `string` | No | Search across first name, last name, course, section, or student ID |
| `course` | `string` | No | Filter by course / program (case-insensitive exact match) |
| `section` | `string` | No | Filter by section (case-insensitive exact match) |
| `sex` | `string` | No | Filter by sex (`Male`, `Female`, `Other`) |

#### Example Request

```http
GET /api/students/?course=BSIT&sex=Male HTTP/1.1
Host: localhost:8000
Accept: application/json
```

#### Response (`200 OK`)

```json
[
  {
    "student_id": 1,
    "first_name": "Juan",
    "last_name": "Dela Cruz",
    "birth_date": "2002-05-15",
    "sex": "Male",
    "course": "BS Information Technology",
    "section": "3A",
    "contact_no": "09123456789",
    "health_records_count": 2,
    "created_at": "2026-08-28T10:00:00Z",
    "updated_at": "2026-08-28T10:30:00Z"
  }
]
```

---

### 2. Create Student

Register a new student in the clinic system.

- **HTTP Method:** `POST`
- **Path:** `/api/students/`
- **Content-Type:** `application/json`

#### Request Body Fields

| Field | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `first_name` | `string` (max 100) | **Yes** | Student's first name |
| `last_name` | `string` (max 100) | **Yes** | Student's last name |
| `course` | `string` (max 100) | **Yes** | Degree program or course (e.g., `BSIT`, `BSCS`, `BSN`) |
| `section` | `string` (max 50) | **Yes** | Class section (e.g., `3A`, `1-1`) |
| `birth_date` | `string` (date: `YYYY-MM-DD`) | No | Date of birth (cannot be in the future) |
| `sex` | `string` | No | `Male`, `Female`, or `Other` |
| `contact_no` | `string` (max 30) | No | Contact telephone or mobile number |

#### Example Request

```json
{
  "first_name": "Juan",
  "last_name": "Dela Cruz",
  "birth_date": "2002-05-15",
  "sex": "Male",
  "course": "BS Information Technology",
  "section": "3A",
  "contact_no": "09123456789"
}
```

#### Response (`201 Created`)

```json
{
  "student_id": 1,
  "first_name": "Juan",
  "last_name": "Dela Cruz",
  "birth_date": "2002-05-15",
  "sex": "Male",
  "course": "BS Information Technology",
  "section": "3A",
  "contact_no": "09123456789",
  "health_records_count": 0,
  "created_at": "2026-08-28T10:00:00Z",
  "updated_at": "2026-08-28T10:00:00Z"
}
```

---

### 3. Retrieve Student Details

Retrieve complete details for a specific student, including their nested list of health records.

- **HTTP Method:** `GET`
- **Path:** `/api/students/{student_id}/`

#### Path Parameters

| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `student_id` | `integer` | **Yes** | Unique auto-incrementing student identifier |

#### Response (`200 OK`)

```json
{
  "student_id": 1,
  "first_name": "Juan",
  "last_name": "Dela Cruz",
  "birth_date": "2002-05-15",
  "sex": "Male",
  "course": "BS Information Technology",
  "section": "3A",
  "contact_no": "09123456789",
  "health_records_count": 1,
  "created_at": "2026-08-28T10:00:00Z",
  "updated_at": "2026-08-28T10:30:00Z",
  "health_records": [
    {
      "health_id": 10,
      "student_id": 1,
      "student_name": "Juan Dela Cruz",
      "allergies": "Penicillin",
      "blood_type": "O+",
      "medical_history": "Mild Asthma",
      "medication": "Salbutamol inhaler as needed",
      "weight": "65.50",
      "height": "172.00",
      "visit": "2026-08-28T09:30:00Z",
      "consultation": "Patient reported mild shortness of breath after physical education. Administered nebulization.",
      "created_at": "2026-08-28T09:35:00Z",
      "updated_at": "2026-08-28T09:35:00Z"
    }
  ]
}
```

---

### 4. Fully Update Student

Replace all writable fields of an existing student.

- **HTTP Method:** `PUT`
- **Path:** `/api/students/{student_id}/`
- **Content-Type:** `application/json`

#### Example Request

```json
{
  "first_name": "Juan",
  "last_name": "Dela Cruz",
  "birth_date": "2002-05-15",
  "sex": "Male",
  "course": "BS Computer Science",
  "section": "4A",
  "contact_no": "09123456780"
}
```

#### Response (`200 OK`)

```json
{
  "student_id": 1,
  "first_name": "Juan",
  "last_name": "Dela Cruz",
  "birth_date": "2002-05-15",
  "sex": "Male",
  "course": "BS Computer Science",
  "section": "4A",
  "contact_no": "09123456780",
  "health_records_count": 1,
  "created_at": "2026-08-28T10:00:00Z",
  "updated_at": "2026-08-28T11:00:00Z"
}
```

---

### 5. Partially Update Student

Update one or more fields of an existing student.

- **HTTP Method:** `PATCH`
- **Path:** `/api/students/{student_id}/`
- **Content-Type:** `application/json`

#### Example Request

```json
{
  "section": "4B",
  "contact_no": "09991112233"
}
```

#### Response (`200 OK`)

```json
{
  "student_id": 1,
  "first_name": "Juan",
  "last_name": "Dela Cruz",
  "birth_date": "2002-05-15",
  "sex": "Male",
  "course": "BS Computer Science",
  "section": "4B",
  "contact_no": "09991112233",
  "health_records_count": 1,
  "created_at": "2026-08-28T10:00:00Z",
  "updated_at": "2026-08-28T11:15:00Z"
}
```

---

### 6. Delete Student

Delete an existing student. Deleting a student cascades and removes all associated health records.

- **HTTP Method:** `DELETE`
- **Path:** `/api/students/{student_id}/`

#### Response (`204 No Content`)

Empty body.

---

### 7. List Health Records for Student

Retrieve all health records for a specific student, ordered by visit date descending.

- **HTTP Method:** `GET`
- **Path:** `/api/students/{student_id}/health-records/`

#### Response (`200 OK`)

```json
[
  {
    "health_id": 10,
    "student_id": 1,
    "student_name": "Juan Dela Cruz",
    "allergies": "Penicillin",
    "blood_type": "O+",
    "medical_history": "Mild Asthma",
    "medication": "Salbutamol inhaler",
    "weight": "65.50",
    "height": "172.00",
    "visit": "2026-08-28T09:30:00Z",
    "consultation": "Routine clinic visit. Vital signs stable.",
    "created_at": "2026-08-28T09:35:00Z",
    "updated_at": "2026-08-28T09:35:00Z"
  }
]
```

---

### 8. Create Health Record for Student

Create a new health record directly associated with the specified student.

- **HTTP Method:** `POST`
- **Path:** `/api/students/{student_id}/health-records/`
- **Content-Type:** `application/json`

#### Example Request

```json
{
  "blood_type": "O+",
  "allergies": "Penicillin",
  "medical_history": "None",
  "medication": "Paracetamol 500mg",
  "weight": "64.00",
  "height": "172.00",
  "visit": "2026-08-28T10:30:00Z",
  "consultation": "Headache and mild fever. Prescribed rest and hydration."
}
```

#### Response (`201 Created`)

```json
{
  "health_id": 11,
  "student_id": 1,
  "student_name": "Juan Dela Cruz",
  "allergies": "Penicillin",
  "blood_type": "O+",
  "medical_history": "None",
  "medication": "Paracetamol 500mg",
  "weight": "64.00",
  "height": "172.00",
  "visit": "2026-08-28T10:30:00Z",
  "consultation": "Headache and mild fever. Prescribed rest and hydration.",
  "created_at": "2026-08-28T10:32:00Z",
  "updated_at": "2026-08-28T10:32:00Z"
}
```

---

## Health Records API

### 1. List Health Records

Retrieve all clinic health records with optional filtering by student ID, blood type, or search terms.

- **HTTP Method:** `GET`
- **Path:** `/api/health-records/`

#### Query Parameters

| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `student_id` | `string` / `integer` | No | Filter records by associated student identifier |
| `blood_type` | `string` | No | Filter by blood type (`A+`, `A-`, `B+`, `B-`, `AB+`, `AB-`, `O+`, `O-`, `Unknown`) |
| `search` | `string` | No | Search across student name, allergies, consultation, or medical history |

#### Response (`200 OK`)

```json
[
  {
    "health_id": 10,
    "student_id": 1,
    "student_name": "Juan Dela Cruz",
    "allergies": "Penicillin",
    "blood_type": "O+",
    "medical_history": "Mild Asthma",
    "medication": "Salbutamol",
    "weight": "65.50",
    "height": "172.00",
    "visit": "2026-08-28T09:30:00Z",
    "consultation": "Patient presented with dizziness.",
    "created_at": "2026-08-28T09:35:00Z",
    "updated_at": "2026-08-28T09:35:00Z"
  }
]
```

---

### 2. Create Health Record

Create a new clinical consultation record.

- **HTTP Method:** `POST`
- **Path:** `/api/health-records/`
- **Content-Type:** `application/json`

#### Request Body Fields

| Field | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `student_id` | `integer` | **Yes** | ID of the student associated with this record |
| `blood_type` | `string` | No | Blood type choice (`A+`, `A-`, `B+`, `B-`, `AB+`, `AB-`, `O+`, `O-`, `Unknown`) |
| `allergies` | `string` | No | Known allergies |
| `medical_history` | `string` | No | Chronic conditions and past illnesses |
| `medication` | `string` | No | Current medications |
| `weight` | `decimal` (0.00 - 500.00) | No | Weight in kilograms (kg) |
| `height` | `decimal` (0.00 - 300.00) | No | Height in centimeters (cm) |
| `visit` | `string` (date-time: ISO 8601) | No | Date and time of consultation (defaults to now) |
| `consultation` | `string` | No | Clinical assessment notes and prescriptions |

#### Example Request

```json
{
  "student_id": 1,
  "blood_type": "O+",
  "allergies": "Penicillin",
  "medical_history": "Mild Asthma",
  "medication": "Salbutamol",
  "weight": "65.50",
  "height": "172.00",
  "visit": "2026-08-28T09:30:00Z",
  "consultation": "Patient reported mild shortness of breath. Vitals normal."
}
```

#### Response (`201 Created`)

```json
{
  "health_id": 10,
  "student_id": 1,
  "student_name": "Juan Dela Cruz",
  "allergies": "Penicillin",
  "blood_type": "O+",
  "medical_history": "Mild Asthma",
  "medication": "Salbutamol",
  "weight": "65.50",
  "height": "172.00",
  "visit": "2026-08-28T09:30:00Z",
  "consultation": "Patient reported mild shortness of breath. Vitals normal.",
  "created_at": "2026-08-28T09:35:00Z",
  "updated_at": "2026-08-28T09:35:00Z"
}
```

---

### 3. Retrieve Health Record

Retrieve details of a single health record by `health_id`.

- **HTTP Method:** `GET`
- **Path:** `/api/health-records/{health_id}/`

#### Path Parameters

| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `health_id` | `integer` | **Yes** | Unique health record identifier |

#### Response (`200 OK`)

```json
{
  "health_id": 10,
  "student_id": 1,
  "student_name": "Juan Dela Cruz",
  "allergies": "Penicillin",
  "blood_type": "O+",
  "medical_history": "Mild Asthma",
  "medication": "Salbutamol",
  "weight": "65.50",
  "height": "172.00",
  "visit": "2026-08-28T09:30:00Z",
  "consultation": "Patient reported mild shortness of breath. Vitals normal.",
  "created_at": "2026-08-28T09:35:00Z",
  "updated_at": "2026-08-28T09:35:00Z"
}
```

---

### 4. Fully Update Health Record

Update all fields of an existing health record.

- **HTTP Method:** `PUT`
- **Path:** `/api/health-records/{health_id}/`
- **Content-Type:** `application/json`

#### Example Request

```json
{
  "student_id": 1,
  "blood_type": "O+",
  "allergies": "Penicillin, Dust",
  "medical_history": "Mild Asthma",
  "medication": "Salbutamol 100mcg",
  "weight": "66.00",
  "height": "172.00",
  "visit": "2026-08-28T09:30:00Z",
  "consultation": "Follow-up consultation. Respiratory exam clear."
}
```

#### Response (`200 OK`)

```json
{
  "health_id": 10,
  "student_id": 1,
  "student_name": "Juan Dela Cruz",
  "allergies": "Penicillin, Dust",
  "blood_type": "O+",
  "medical_history": "Mild Asthma",
  "medication": "Salbutamol 100mcg",
  "weight": "66.00",
  "height": "172.00",
  "visit": "2026-08-28T09:30:00Z",
  "consultation": "Follow-up consultation. Respiratory exam clear.",
  "created_at": "2026-08-28T09:35:00Z",
  "updated_at": "2026-08-28T10:00:00Z"
}
```

---

### 5. Partially Update Health Record

Partially update one or more fields of an existing health record.

- **HTTP Method:** `PATCH`
- **Path:** `/api/health-records/{health_id}/`
- **Content-Type:** `application/json`

#### Example Request

```json
{
  "weight": "66.20",
  "consultation": "Updated vitals and notes."
}
```

#### Response (`200 OK`)

```json
{
  "health_id": 10,
  "student_id": 1,
  "student_name": "Juan Dela Cruz",
  "allergies": "Penicillin, Dust",
  "blood_type": "O+",
  "medical_history": "Mild Asthma",
  "medication": "Salbutamol 100mcg",
  "weight": "66.20",
  "height": "172.00",
  "visit": "2026-08-28T09:30:00Z",
  "consultation": "Updated vitals and notes.",
  "created_at": "2026-08-28T09:35:00Z",
  "updated_at": "2026-08-28T10:05:00Z"
}
```

---

### 6. Delete Health Record

Delete an existing health record.

- **HTTP Method:** `DELETE`
- **Path:** `/api/health-records/{health_id}/`

#### Response (`204 No Content`)

Empty body.

---

## System & Discovery Endpoints

### 1. API Root / Discovery Endpoint

- **HTTP Method:** `GET`
- **Path:** `/`

#### Response (`200 OK`)

```json
{
  "name": "IDSC Clinic System API",
  "version": "1.0.0",
  "status": "healthy",
  "endpoints": {
    "students": "/api/students/",
    "health_records": "/api/health-records/",
    "student_health_records": "/api/students/<student_id>/health-records/",
    "schema": "/api/schema/",
    "docs": "/api/docs/",
    "redoc": "/api/redoc/",
    "admin": "/admin/"
  }
}
```

### 2. OpenAPI Schema

- **HTTP Method:** `GET`
- **Path:** `/api/schema/`
- **Format:** OpenAPI 3.0 YAML / JSON download

### 3. Swagger UI

- **HTTP Method:** `GET`
- **Path:** `/api/docs/`
- **Format:** Interactive HTML Swagger UI

### 4. ReDoc UI

- **HTTP Method:** `GET`
- **Path:** `/api/redoc/`
- **Format:** Interactive HTML ReDoc UI
