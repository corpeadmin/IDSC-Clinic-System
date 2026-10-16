export type Student = {
  student_id: string
  first_name: string
  last_name: string
  course: string
  section: string
  status: "ACTIVE" | "INACTIVE" | "GRADUATED"
}
export type HealthRecord = {
  health_record_id: number
  student_id: string
  blood_type: string | null
  allergies: string
  medical_history: string
  current_medications: string
  height_cm: number | null
  weight_kg: number | null
  created_at: string
  updated_at: string
}
export type Consultation = {
  consultation_id: number
  student_id: string
  chief_complaint: string
  assessment: string
  treatment: string
  notes: string
  consulted_at: string
  created_at: string
  updated_at: string
}
export type HealthStatus = {
  status_id: number
  student_id: string
  status: "CLEARED" | "RESTRICTED" | "UNDER_OBSERVATION"
  remarks: string
  effective_at: string
  created_at: string
  updated_at: string
}
export type Medicine = {
  medicine_id: string
  name: string
  generic_name: string
  unit: string
  quantity_in_stock: number
  reorder_level: number
  is_low_stock: boolean
  status: "ACTIVE" | "INACTIVE"
}
export type ClinicUser = {
  user_id: number
  username: string
  first_name: string
  last_name: string
  email: string
  role: "ADMIN" | "STAFF" | null
  is_active: boolean
}
export type Activity = {
  activity_type: "HEALTH_RECORD" | "CONSULTATION" | "HEALTH_STATUS" | "MEDICINE_DISPENSATION" | "MEDICINE_DISPENSATION_ROLLBACK"
  reference_id: number
  student_id: string
  occurred_at: string
}

export const students: Student[] = [
  {
    student_id: "2026-0001",
    first_name: "Juan",
    last_name: "Dela Cruz",
    course: "BSIT",
    section: "3A",
    status: "ACTIVE",
  },
  {
    student_id: "2026-0002",
    first_name: "Maria",
    last_name: "Santos",
    course: "BSCS",
    section: "2B",
    status: "ACTIVE",
  },
  {
    student_id: "2026-0003",
    first_name: "Pedro",
    last_name: "Reyes",
    course: "BSIT",
    section: "4A",
    status: "GRADUATED",
  },
]
export const healthRecords: HealthRecord[] = [
  {
    health_record_id: 1,
    student_id: "2026-0001",
    blood_type: "O+",
    allergies: "Penicillin",
    medical_history: "History of asthma",
    current_medications: "None",
    height_cm: 170.5,
    weight_kg: 65.2,
    created_at: "2026-09-29T14:00:00+08:00",
    updated_at: "2026-09-29T14:00:00+08:00",
  },
]
export const consultations: Consultation[] = [
  {
    consultation_id: 1,
    student_id: "2026-0001",
    chief_complaint: "Headache and dizziness",
    assessment: "Possible tension headache",
    treatment: "Rest and hydration advised",
    notes: "Return if symptoms persist",
    consulted_at: "2026-09-29T14:05:00+08:00",
    created_at: "2026-09-29T14:05:00+08:00",
    updated_at: "2026-09-29T14:05:00+08:00",
  },
  {
    consultation_id: 2,
    student_id: "2026-0002",
    chief_complaint: "Mild fever",
    assessment: "Possible viral infection",
    treatment: "Rest and hydration advised",
    notes: "Monitor temperature",
    consulted_at: "2026-09-29T15:00:00+08:00",
    created_at: "2026-09-29T15:00:00+08:00",
    updated_at: "2026-09-29T15:00:00+08:00",
  },
]
export const healthStatuses: HealthStatus[] = [
  {
    status_id: 1,
    student_id: "2026-0001",
    status: "CLEARED",
    remarks: "Cleared for regular school activities",
    effective_at: "2026-09-29T14:10:00+08:00",
    created_at: "2026-09-29T14:10:00+08:00",
    updated_at: "2026-09-29T14:10:00+08:00",
  },
]
export const medicines: Medicine[] = [
  {
    medicine_id: "MED-0001",
    name: "Paracetamol",
    generic_name: "Paracetamol",
    unit: "tablet",
    quantity_in_stock: 100,
    reorder_level: 20,
    is_low_stock: false,
    status: "ACTIVE",
  },
  {
    medicine_id: "MED-0002",
    name: "Ibuprofen",
    generic_name: "Ibuprofen",
    unit: "tablet",
    quantity_in_stock: 15,
    reorder_level: 20,
    is_low_stock: true,
    status: "ACTIVE",
  },
  {
    medicine_id: "MED-0003",
    name: "Cetirizine",
    generic_name: "Cetirizine",
    unit: "tablet",
    quantity_in_stock: 0,
    reorder_level: 10,
    is_low_stock: true,
    status: "ACTIVE",
  },
]
export const users: ClinicUser[] = [
  {
    user_id: 12,
    username: "clinic.staff",
    first_name: "Maria",
    last_name: "Santos",
    email: "maria.santos@example.edu",
    role: "STAFF",
    is_active: true,
  },
]
export const dashboard = {
  summary: {
    total_students: 1200,
    total_health_records: 850,
    total_medicine_stock: 540,
    low_stock_medicines: 3,
  },
  recent_activity: [
    {
      activity_type: "CONSULTATION",
      reference_id: 18,
      student_id: "2026-0001",
      occurred_at: "2026-09-29T13:50:00+08:00",
    },
  ] as Activity[],
}
