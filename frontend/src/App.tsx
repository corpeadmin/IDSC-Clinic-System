import {
  useEffect,
  useRef,
  useState,
  type FormEvent,
  type ReactNode,
} from "react"
import * as seed from "./data"
import idscLogo from "./assets/idsc-logo.png"
import type {
  Activity,
  ClinicUser,
  Consultation,
  HealthRecord,
  HealthStatus,
  Medicine,
  Student,
} from "./data"

type IconName = "grid" | "students" | "record" | "pill" | "settings" | "shield" | "logout" | "chevron" | "arrow" | "search" | "plus" | "close" | "check" | "clock" | "calendar" | "activity" | "alert" | "edit" | "trash" | "refresh" | "lock" | "eye" | "menu"
const paths: Record<IconName, ReactNode> = {
  grid: (
    <>
      <rect x="3" y="3" width="7" height="7" rx="1.5" />
      <rect x="14" y="3" width="7" height="7" rx="1.5" />
      <rect x="3" y="14" width="7" height="7" rx="1.5" />
      <rect x="14" y="14" width="7" height="7" rx="1.5" />
    </>
  ),
  students: (
    <>
      <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2m20 0v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75" />
      <circle cx="9" cy="7" r="4" />
    </>
  ),
  record: (
    <>
      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8Zm0 0v6h6M8 13h8M8 17h5" />
    </>
  ),
  pill: (
    <>
      <path d="m9 15 6-6M4.5 19.5a5 5 0 0 1 0-7l8-8a5 5 0 0 1 7 7l-8 8a5 5 0 0 1-7 0Z" />
    </>
  ),
  settings: (
    <>
      <path d="m9 3-1 3-3 1-2 3 2 2-1 3 2 3 3-1 2 3h3l1-3 3-1 2-3-2-2 1-3-2-3-3 1-2-3Z" />
      <circle cx="12" cy="12" r="3" />
    </>
  ),
  shield: (
    <>
      <path d="m12 3 8 3v6c0 5-8 9-8 9s-8-4-8-9V6Z" />
      <path d="m8 12 3 3 5-6" />
    </>
  ),
  logout: (
    <>
      <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4m7 14 5-5-5-5M21 12H9" />
    </>
  ),
  chevron: <path d="m9 5 7 7-7 7" />,
  arrow: <path d="M4 12h16m-6-6 6 6-6 6" />,
  search: (
    <>
      <circle cx="10.5" cy="10.5" r="6.5" />
      <path d="m16 16 5 5" />
    </>
  ),
  plus: <path d="M12 5v14M5 12h14" />,
  close: <path d="m6 6 12 12M6 18 18 6" />,
  check: <path d="m5 12 4 4L19 6" />,
  clock: (
    <>
      <circle cx="12" cy="12" r="9" />
      <path d="M12 7v5l3 2" />
    </>
  ),
  calendar: (
    <>
      <rect x="3" y="5" width="18" height="16" rx="2" />
      <path d="M16 3v4M8 3v4M3 11h18" />
    </>
  ),
  activity: <path d="M2 12h5l3-8 4 16 3-8h5" />,
  alert: (
    <>
      <path d="m10.3 4-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.7-3l-8-14a2 2 0 0 0-3.4 0ZM12 9v4m0 4h.01" />
    </>
  ),
  edit: (
    <>
      <path d="m16 3 5 5-12 12-6 1 1-6Zm-2 2 5 5" />
    </>
  ),
  trash: (
    <>
      <path d="M3 6h18M9 6V3h6v3M5 6l1 15h12l1-15M10 10v7m4-7v7" />
    </>
  ),
  refresh: (
    <>
      <path d="M20 7v5h-5M4 17v-5h5M5 8a8 8 0 0 1 13-3l2 3M4 16l2 3a8 8 0 0 0 13-3" />
    </>
  ),
  lock: (
    <>
      <rect x="4" y="10" width="16" height="11" rx="2" />
      <path d="M8 10V7a4 4 0 0 1 8 0v3m-4 4v3" />
    </>
  ),
  eye: (
    <>
      <path d="M2 12s4-7 10-7 10 7 10 7-4 7-10 7S2 12 2 12Z" />
      <circle cx="12" cy="12" r="3" />
    </>
  ),
  menu: <path d="M4 6h16M4 12h16M4 18h16" />,
}
function Icon({ name, size = 20 }: { name: IconName size?: number }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.65"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      {paths[name]}
    </svg>
  )
}
function Logo() {
  return (
    <div className="brand">
      <img
        className="brand-symbol"
        src={idscLogo}
        alt="Infotech Development Systems Colleges logo"
      />
      <div>
        <strong>IDSC Clinic</strong>
        <small>HEALTH MANAGEMENT</small>
      </div>
    </div>
  )
}
function Badge({ value }: { value: string }) {
  const tone = ["ACTIVE", "CLEARED", "Available", "COMPLETED"].includes(value)
    ? "green"
    : ["Low stock", "RESTRICTED", "UNDER_OBSERVATION"].includes(value)
      ? "amber"
      : "gray"
  return (
    <span className={`badge ${tone}`}>
      <i />
      {value
        .replaceAll("_", " ")
        .toLowerCase()
        .replace(/^./, (x) => x.toUpperCase())}
    </span>
  )
}
function Button({
  children,
  onClick,
  variant = "primary",
  icon,
  type = "button",
  disabled = false,
}: {
  children: ReactNode
  onClick?: () => void
  variant?: "primary" | "secondary" | "danger" | "text"
  icon?: IconName
  type?: "button" | "submit"
  disabled?: boolean
}) {
  return (
    <button
      type={type}
      className={`button ${variant}`}
      onClick={onClick}
      disabled={disabled}
    >
      {icon && <Icon name={icon} size={17} />}
      {children}
    </button>
  )
}
function Search({
  value,
  onChange,
  placeholder,
}: {
  value: string
  onChange: (v: string) => void
  placeholder: string
}) {
  return (
    <div className="search">
      <Icon name="search" size={18} />
      <input
        aria-label={placeholder}
        placeholder={placeholder}
        value={value}
        onChange={(e) => onChange(e.target.value)}
      />
      {value && (
        <button aria-label="Clear search" onClick={() => onChange("")}>
          <Icon name="close" size={15} />
        </button>
      )}
    </div>
  )
}
function Empty({
  text = "No records found",
  detail = "Try another search or add a new record.",
}: {
  text?: string
  detail?: string
}) {
  return (
    <div className="empty">
      <Icon name="record" size={30} />
      <h3>{text}</h3>
      <p>{detail}</p>
    </div>
  )
}
function Modal({
  title,
  children,
  onClose,
}: {
  title: string
  children: ReactNode
  onClose: () => void
}) {
  const ref = useRef<HTMLDivElement>(null)
  useEffect(() => {
    const previous = document.activeElement as HTMLElement
    const panel = ref.current
    panel
      ?.querySelector<HTMLElement>("input, select, textarea, button")
      ?.focus()
    function key(e: KeyboardEvent) {
      if (e.key === "Escape") onClose()
      if (e.key === "Tab" && panel) {
        const items = Array.from(
          panel.querySelectorAll<HTMLElement>(
            "button:not(:disabled), input, select, textarea, [tabindex='0']",
          ),
        )
        const first = items[0],
          last = items[items.length - 1]
        if (e.shiftKey && document.activeElement === first) {
          e.preventDefault()
          last?.focus()
        } else if (!e.shiftKey && document.activeElement === last) {
          e.preventDefault()
          first?.focus()
        }
      }
    }
    document.addEventListener("keydown", key)
    return () => {
      document.removeEventListener("keydown", key)
      previous?.focus()
    }
  }, [onClose])
  return (
    <div
      className="modal-backdrop"
      onMouseDown={(e) => {
        if (e.target === e.currentTarget) onClose()
      }}
    >
      <div
        ref={ref}
        className="modal"
        role="dialog"
        aria-modal="true"
        aria-label={title}
      >
        <div className="modal-heading">
          <h2>{title}</h2>
          <button
            className="icon-button"
            aria-label="Close dialog"
            onClick={onClose}
          >
            <Icon name="close" />
          </button>
        </div>
        {children}
      </div>
    </div>
  )
}
function Field({
  label,
  name,
  value,
  type = "text",
  required = false,
  options,
  multiline = false,
  min,
  max,
}: {
  label: string
  name: string
  value?: string | number | null
  type?: string
  required?: boolean
  options?: string[]
  multiline?: boolean
  min?: number
  max?: number
}) {
  return (
    <label className="field">
      <span>
        {label}
        {required && <em> *</em>}
      </span>
      {options ? (
        <select name={name} defaultValue={value ?? options[0]}>
          {options.map((x) => (
            <option key={x} value={x}>
              {x.replaceAll("_", " ")}
            </option>
          ))}
        </select>
      ) : multiline ? (
        <textarea
          name={name}
          defaultValue={value ?? ""}
          rows={3}
          required={required}
        />
      ) : (
        <input
          name={name}
          type={type}
          defaultValue={value ?? ""}
          required={required}
          min={min}
          max={max}
          step={type === "number" ? "0.01" : undefined}
          maxLength={
            name === "email"
              ? 254
              : name === "username" ||
                  name === "first_name" ||
                  name === "last_name"
                ? 150
                : undefined
          }
        />
      )}
    </label>
  )
}
const date = (value: string, time = false) =>
  new Intl.DateTimeFormat("en-US", {
    timeZone: "Asia/Manila",
    month: "short",
    day: "numeric",
    year: time ? undefined : "numeric",
    ...(time ? { hour: "numeric", minute: "2-digit" } : {}),
  }).format(new Date(value))
const fullname = (student: Student) =>
  `${student.first_name} ${student.last_name}`
const activityLabels: Record<Activity["activity_type"], string> = {
  CONSULTATION: "Consultation recorded",
  HEALTH_RECORD: "Health record created",
  HEALTH_STATUS: "Health status recorded",
  MEDICINE_DISPENSATION: "Medicine dispensed",
  MEDICINE_DISPENSATION_ROLLBACK: "Dispensation rolled back",
}
type Page = "dashboard" | "students" | "medicines" | "settings" | "admin"
type Editor = {
  kind: "record" | "consultation" | "status" | "user"
  existing?: HealthRecord | Consultation | HealthStatus | ClinicUser
}

export default function App() {
  const [page, setPage] = useState<Page>("dashboard")
  const [loggedIn, setLoggedIn] = useState(false)
  const [selected, setSelected] = useState<Student | null>(null)
  const [records, setRecords] = useState(seed.healthRecords)
  const [visits, setVisits] = useState(seed.consultations)
  const [statuses, setStatuses] = useState(seed.healthStatuses)
  const [users, setUsers] = useState(seed.users)
  const [activities, setActivities] = useState(seed.dashboard.recent_activity)
  const [search, setSearch] = useState("")
  const [filter, setFilter] = useState("All")
  const [tab, setTab] = useState("Health record")
  const [editor, setEditor] = useState<Editor | null>(null)
  const [confirmation, setConfirmation] = useState<{
    title: string
    action: () => void
  } | null>(null)
  const [medicine, setMedicine] = useState<Medicine | null>(null)
  const [toast, setToast] = useState("")
  const [menuOpen, setMenuOpen] = useState(false)
  const [loginError, setLoginError] = useState("")
  const [info, setInfo] = useState("")
  useEffect(() => {
    if (toast) {
      const t = setTimeout(() => setToast(""), 4500)
      return () => clearTimeout(t)
    }
  }, [toast])
  function navigate(next: Page) {
    setPage(next)
    setSelected(null)
    setSearch("")
    setFilter("All")
    setMenuOpen(false)
  }
  function openStudent(s: Student) {
    setSelected(s)
    setPage("students")
    setTab("Health record")
    setSearch("")
  }
  const navigation: { id: Page label: string icon: IconName }[] = [
    { id: "dashboard", label: "Dashboard", icon: "grid" },
    { id: "students", label: "Students", icon: "students" },
    { id: "medicines", label: "Medicine stock", icon: "pill" },
    { id: "settings", label: "Settings", icon: "settings" },
    { id: "admin", label: "Administration", icon: "shield" },
  ]
  function saveEditor(e: FormEvent<HTMLFormElement>) {
    e.preventDefault()
    if (!editor) return
    const form = Object.fromEntries(
      new FormData(e.currentTarget).entries(),
    ) as Record<string, string>
    const now = new Date().toISOString()
    let reference = 0
    let activityType: Activity["activity_type"] = "HEALTH_RECORD"
    if (
      editor.kind !== "user" &&
      selected?.status !== "ACTIVE" &&
      !editor.existing
    ) {
      setToast("Only active students can receive new clinic records.")
      return
    }
    if (editor.kind === "record" && selected) {
      const existing = editor.existing as HealthRecord | undefined
      reference =
        existing?.health_record_id ??
        Math.max(0, ...records.map((r) => r.health_record_id)) + 1
      const record: HealthRecord = {
        health_record_id: reference,
        student_id: selected.student_id,
        blood_type: form.blood_type,
        allergies: form.allergies,
        medical_history: form.medical_history,
        current_medications: form.current_medications,
        height_cm: form.height_cm ? Number(form.height_cm) : null,
        weight_kg: form.weight_kg ? Number(form.weight_kg) : null,
        created_at: existing?.created_at ?? now,
        updated_at: now,
      }
      setRecords(
        existing
          ? records.map((r) => (r.health_record_id === reference ? record : r))
          : [...records, record],
      )
    } else if (editor.kind === "consultation" && selected) {
      if (!form.chief_complaint.trim()) {
        setToast("Chief complaint cannot be blank.")
        return
      }
      const existing = editor.existing as Consultation | undefined
      reference =
        existing?.consultation_id ??
        Math.max(0, ...visits.map((r) => r.consultation_id)) + 1
      const visit: Consultation = {
        consultation_id: reference,
        student_id: selected.student_id,
        chief_complaint: form.chief_complaint.trim(),
        assessment: form.assessment,
        treatment: form.treatment,
        notes: form.notes,
        consulted_at: existing?.consulted_at ?? now,
        created_at: existing?.created_at ?? now,
        updated_at: now,
      }
      setVisits(
        existing
          ? visits.map((v) => (v.consultation_id === reference ? visit : v))
          : [visit, ...visits],
      )
      activityType = "CONSULTATION"
    } else if (editor.kind === "status" && selected) {
      const existing = editor.existing as HealthStatus | undefined
      reference =
        existing?.status_id ??
        Math.max(0, ...statuses.map((r) => r.status_id)) + 1
      const status: HealthStatus = {
        status_id: reference,
        student_id: selected.student_id,
        status: form.status as HealthStatus["status"],
        remarks: form.remarks,
        effective_at: existing?.effective_at ?? now,
        created_at: existing?.created_at ?? now,
        updated_at: now,
      }
      setStatuses(
        existing
          ? statuses.map((s) => (s.status_id === reference ? status : s))
          : [status, ...statuses],
      )
      activityType = "HEALTH_STATUS"
    } else if (editor.kind === "user") {
      const existing = editor.existing as ClinicUser | undefined
      if (!existing && users.some((u) => u.username === form.username.trim())) {
        setToast("This username is already in use.")
        return
      }
      const user: ClinicUser = {
        user_id:
          existing?.user_id ?? Math.max(0, ...users.map((u) => u.user_id)) + 1,
        username: existing?.username ?? form.username.trim(),
        first_name: form.first_name,
        last_name: form.last_name,
        email: form.email,
        role: existing?.role ?? "STAFF",
        is_active: existing?.is_active ?? true,
      }
      if (!user.username) {
        setToast("Username cannot be blank.")
        return
      }
      setUsers(
        existing
          ? users.map((u) => (u.user_id === user.user_id ? user : u))
          : [...users, user],
      )
    }
    if (selected && !editor.existing && editor.kind !== "user")
      setActivities([
        {
          activity_type: activityType,
          reference_id: reference,
          student_id: selected.student_id,
          occurred_at: now,
        },
        ...activities,
      ])
    setEditor(null)
    setToast(
      `${
        editor.existing ? "Changes saved" : "Record created"
      } in the demo workspace.`,
    )
  }
  function deleteRecord(
    kind: "record" | "consultation" | "status",
    id: number,
  ) {
    setConfirmation({
      title: `Delete this ${
        kind === "record"
          ? "health record"
          : kind === "status"
            ? "health status"
            : "consultation"
      }?`,
      action: () => {
        if (kind === "record")
          setRecords(records.filter((r) => r.health_record_id !== id))
        if (kind === "consultation")
          setVisits(visits.filter((r) => r.consultation_id !== id))
        if (kind === "status")
          setStatuses(statuses.filter((r) => r.status_id !== id))
        setToast("Record deleted from the demo workspace.")
      },
    })
  }
  const title = selected
    ? "Student health record"
    : navigation.find((n) => n.id === page)!.label
  const sampleSummary = seed.dashboard.summary
  const lowStock = seed.medicines.filter((m) => m.is_low_stock)
  const studentRecords = records.filter(
    (r) => r.student_id === selected?.student_id,
  )
  const studentVisits = visits.filter(
    (r) =>
      r.student_id === selected?.student_id &&
      `${r.chief_complaint} ${r.assessment} ${r.treatment} ${r.notes}`
        .toLowerCase()
        .includes(search.toLowerCase()),
  )
  const studentStatuses = statuses.filter(
    (r) => r.student_id === selected?.student_id,
  )
  const filteredStudents = seed.students.filter(
    (s) =>
      `${fullname(s)} ${s.student_id} ${s.course} ${s.section}`
        .toLowerCase()
        .includes(search.toLowerCase()) &&
      (filter === "All" || s.course === filter),
  )
  const filteredMedicines = seed.medicines.filter(
    (m) =>
      `${m.name} ${m.generic_name} ${m.medicine_id}`
        .toLowerCase()
        .includes(search.toLowerCase()) &&
      (filter === "All" ||
        (filter === "Low stock" ? m.is_low_stock : m.quantity_in_stock > 0)),
  )
  const filteredUsers = users.filter((u) =>
    `${u.username} ${u.first_name} ${u.last_name} ${u.email}`
      .toLowerCase()
      .includes(search.toLowerCase()),
  )

  if (!loggedIn)
    return (
      <div className="login-page">
        <div className="login-form-wrap">
          <form
            className="login-form"
            onSubmit={(e) => {
              e.preventDefault()
              const credentials = new FormData(e.currentTarget)
              if (
                credentials.get("email") !== "admin" ||
                credentials.get("password") !== "admin123"
              ) {
                setLoginError("Invalid email or password.")
                return
              }
              setLoginError("")
              setLoggedIn(true)
              navigate("dashboard")
            }}
          >
            <div className="login-brand">
              <Logo />
            </div>
            <span className="eyebrow">WELCOME BACK</span>
            <h2>Log in to your account</h2>
            <p>Access your clinic workspace.</p>
            <Field label="Email" name="email" required />
            <Field label="Password" name="password" type="password" required />
            <div className="login-forgot-row">
              <button className="text-link" type="button" disabled>
                Forgot password?
              </button>
            </div>
            {loginError && (
              <div className="notice" role="alert">
                {loginError}
              </div>
            )}
            <Button type="submit" icon="arrow">
              Log in
            </Button>
          </form>
        </div>
      </div>
    )

  return (
    <div className="app-shell">
      {menuOpen && (
        <div className="sidebar-scrim" onClick={() => setMenuOpen(false)} />
      )}
      <aside className={`sidebar ${menuOpen ? "open" : ""}`}>
        <Logo />
        <div className="workspace-label">WORKSPACE</div>
        <nav aria-label="Main navigation">
          {navigation.slice(0, 3).map((n) => (
            <button
              key={n.id}
              className={`nav-item ${page === n.id ? "active" : ""}`}
              onClick={() => navigate(n.id)}
            >
              <Icon name={n.icon} />
              <span>{n.label}</span>
              {page === n.id && <i />}
            </button>
          ))}
          <div className="nav-divider" />
          <div className="workspace-label">MANAGEMENT</div>
          {navigation.slice(3).map((n) => (
            <button
              key={n.id}
              className={`nav-item ${page === n.id ? "active" : ""}`}
              onClick={() => navigate(n.id)}
            >
              <Icon name={n.icon} />
              <span>{n.label}</span>
              {page === n.id && <i />}
            </button>
          ))}
        </nav>
        <div className="sidebar-bottom">
          <div className="care-card">
            <div className="care-icon">
              <Icon name="shield" size={21} />
            </div>
            <h3>Care starts here.</h3>
            <p>
              Supporting a healthier
              <br />
              student community.
            </p>
            <span>
              IDSC Clinic System <Icon name="activity" size={15} />
            </span>
          </div>
          <button
            className="nav-item logout"
            onClick={() => {
              setLoggedIn(false)
              setMenuOpen(false)
            }}
          >
            <Icon name="logout" />
            <span>Log out</span>
          </button>
          <div className="sidebar-version">
            CLINIC SYSTEM <span>v1.0</span>
          </div>
        </div>
      </aside>
      <div className="main-shell">
        <header className="topbar">
          <div className="topbar-left">
            <button
              className="icon-button mobile-menu"
              aria-label="Open navigation"
              onClick={() => setMenuOpen(true)}
            >
              <Icon name="menu" />
            </button>
            <span className="breadcrumb">Workspace</span>
            <Icon name="chevron" size={13} />
            <strong>{title}</strong>
          </div>
          <div className="topbar-right">
            <span className="demo-label">
              <i /> Demo workspace
            </span>
            <div className="topbar-separator" />
            <button className="profile" onClick={() => navigate("settings")}>
              <div className="avatar">CS</div>
              <div>
                <strong>clinic_staff</strong>
                <span>Clinic account</span>
              </div>
              <Icon name="chevron" size={15} />
            </button>
          </div>
        </header>
        <main>
          {page === "dashboard" && (
            <>
              <div className="page-heading">
                <div>
                  <div className="eyebrow">YOUR CLINIC AT A GLANCE</div>
                  <h1>Dashboard</h1>
                  <p>An overview of your campus health and clinic activity.</p>
                </div>
                <div className="date-chip">
                  <Icon name="calendar" size={17} />
                  September 29, 2026
                </div>
              </div>
              <section className="welcome-banner">
                <div className="banner-copy">
                  <span className="banner-tag">
                    <i /> STUDENT WELLNESS, FIRST
                  </span>
                  <h2>Good care starts with a clear picture.</h2>
                  <p>
                    Keep health records organized and every student’s well-being
                    in focus.
                  </p>
                  <Button
                    variant="secondary"
                    onClick={() => navigate("students")}
                    icon="students"
                  >
                    View students <Icon name="arrow" size={16} />
                  </Button>
                </div>
                <div className="banner-art" aria-hidden="true">
                  <div className="art-orbit orbit-one" />
                  <div className="art-orbit orbit-two" />
                  <div className="art-cross">
                    <span />
                    <span />
                  </div>
                  <div className="art-leaf leaf-one" />
                  <div className="art-leaf leaf-two" />
                  <div className="art-dot dot-one" />
                  <div className="art-dot dot-two" />
                </div>
              </section>
              <div className="stats-grid">
                {([
                  {
                    label: "Total students",
                    value: sampleSummary.total_students,
                    icon: "students",
                    source: "Registrar integration",
                    link: "students",
                  },
                  {
                    label: "Health records",
                    value:
                      sampleSummary.total_health_records +
                      records.length -
                      seed.healthRecords.length,
                    icon: "record",
                    source: "Clinic-managed records",
                    link: "students",
                  },
                  {
                    label: "Total medicine stock",
                    value: sampleSummary.total_medicine_stock,
                    icon: "pill",
                    source: "Units from Inventory",
                    link: "medicines",
                  },
                  {
                    label: "Low-stock medicines",
                    value: sampleSummary.low_stock_medicines,
                    icon: "alert",
                    source: "At or below reorder level",
                    link: "medicines",
                  },
                ] as const).map((s, index) => (
                  <button
                    key={s.label}
                    className={`stat-card ${index === 3 ? "warning-stat" : ""}`}
                    onClick={() => {
                      navigate(s.link)
                      if (index === 3) setFilter("Low stock")
                    }}
                  >
                    <div className="stat-top">
                      <span>{s.label}</span>
                      <div className="stat-icon">
                        <Icon name={s.icon} size={21} />
                      </div>
                    </div>
                    <strong className="stat-value">
                      {s.value.toLocaleString()}
                    </strong>
                    <div className="stat-bottom">
                      <span>{s.source}</span>
                      <Icon name="arrow" size={15} />
                    </div>
                  </button>
                ))}
              </div>
              <div className="dashboard-columns">
                <section className="panel activity-panel">
                  <div className="panel-heading">
                    <div>
                      <h2>Recent activity</h2>
                      <p>The latest updates from your clinic.</p>
                    </div>
                    <span className="subtle-chip">Clinic activity</span>
                  </div>
                  <div className="activity-list">
                    {activities.map((a, index) => {
                      const student = seed.students.find(
                        (s) => s.student_id === a.student_id,
                      )
                      return (
                        <div
                          className="activity-row"
                          key={`${a.activity_type}-${a.reference_id}-${index}`}
                        >
                          <div className="activity-icon">
                            <Icon
                              name={
                                a.activity_type === "CONSULTATION"
                                  ? "activity"
                                  : a.activity_type === "HEALTH_STATUS"
                                    ? "shield"
                                    : "record"
                              }
                            />
                          </div>
                          <div className="activity-text">
                            <h3>{activityLabels[a.activity_type]}</h3>
                            <p>
                              {student ? fullname(student) : a.student_id}
                              <span>·</span>
                              {a.student_id}
                            </p>
                            <small>Reference #{a.reference_id}</small>
                          </div>
                          <div className="activity-time">
                            <span>{date(a.occurred_at, true)}</span>
                            <button
                              className="text-link"
                              onClick={() => {
                                if (student) {
                                  openStudent(student)
                                  setTab(
                                    a.activity_type === "CONSULTATION"
                                      ? "Consultations"
                                      : a.activity_type === "HEALTH_STATUS"
                                        ? "Health status"
                                        : "Health record",
                                  )
                                }
                              }}
                            >
                              View student <Icon name="arrow" size={14} />
                            </button>
                          </div>
                        </div>
                      )
                    })}
                  </div>
                  <div className="panel-foot">
                    <Icon name="clock" size={15} />
                    <span>
                      Activity timestamps are shown in Philippine time.
                    </span>
                  </div>
                </section>
                <section className="panel stock-panel">
                  <div className="panel-heading">
                    <div>
                      <h2>Stock attention</h2>
                      <p>Medicines that need a closer look.</p>
                    </div>
                    <span className="attention-dot">
                      <Icon name="alert" size={18} />
                    </span>
                  </div>
                  <div className="stock-list">
                    {lowStock.map((m) => (
                      <button
                        className="stock-row"
                        key={m.medicine_id}
                        onClick={() => setMedicine(m)}
                      >
                        <div
                          className={`medicine-icon ${
                            m.quantity_in_stock === 0 ? "muted" : ""
                          }`}
                        >
                          <Icon name="pill" size={19} />
                        </div>
                        <div className="stock-name">
                          <strong>{m.name}</strong>
                          <span>{m.medicine_id}</span>
                        </div>
                        <div className="stock-quantity">
                          <strong>
                            {m.quantity_in_stock} <small>{m.unit}s</small>
                          </strong>
                          <span>
                            {m.quantity_in_stock === 0
                              ? "Out of stock"
                              : "Low stock"}
                          </span>
                        </div>
                      </button>
                    ))}
                  </div>
                  <div className="stock-panel-note">
                    <Icon name="refresh" size={14} />
                    Read-only data from Inventory
                  </div>
                  <button
                    className="panel-link"
                    onClick={() => navigate("medicines")}
                  >
                    View medicine stock
                    <Icon name="arrow" size={16} />
                  </button>
                </section>
              </div>
              <section className="quick-section">
                <div className="section-title">
                  <h2>Quick access</h2>
                  <span>Your everyday clinic tasks, a little closer.</span>
                </div>
                <div className="quick-grid">
                  {([
                    {
                      icon: "students",
                      title: "Student health records",
                      desc: "Find a student and manage their care.",
                      page: "students",
                    },
                    {
                      icon: "pill",
                      title: "Medicine inventory",
                      desc: "Check availability and stock levels.",
                      page: "medicines",
                    },
                    {
                      icon: "shield",
                      title: "User administration",
                      desc: "Manage clinic staff accounts.",
                      page: "admin",
                    },
                  ] as const).map((q) => (
                    <button
                      className="quick-card"
                      key={q.title}
                      onClick={() => navigate(q.page)}
                    >
                      <div className="quick-icon">
                        <Icon name={q.icon} size={21} />
                      </div>
                      <div>
                        <h3>{q.title}</h3>
                        <p>{q.desc}</p>
                      </div>
                      <Icon name="chevron" size={17} />
                    </button>
                  ))}
                </div>
              </section>
              <div className="sample-note">
                <Icon name="eye" size={14} />
                <span>
                  API example data. Dashboard totals and list examples are
                  separate sample responses, not a complete dataset.
                </span>
              </div>
            </>
          )}

          {page === "students" && !selected && (
            <>
              <div className="page-heading">
                <div>
                  <div className="eyebrow">STUDENT CARE</div>
                  <h1>Students</h1>
                  <p>Find a student to view and manage their clinic records.</p>
                </div>
                <span className="integration-chip">
                  <Icon name="lock" size={14} />
                  Registrar · Read-only
                </span>
              </div>
              <section className="panel">
                <div className="table-toolbar">
                  <Search
                    value={search}
                    onChange={setSearch}
                    placeholder="Search name, student ID, course..."
                  />
                  <div className="filter-control">
                    <span>Course</span>
                    <select
                      aria-label="Filter course"
                      value={filter}
                      onChange={(e) => setFilter(e.target.value)}
                    >
                      <option value="All">All courses</option>
                      <option>BSIT</option>
                      <option>BSCS</option>
                    </select>
                  </div>
                </div>
                <div className="table-scroll">
                  <table>
                    <thead>
                      <tr>
                        <th>Student</th>
                        <th>Student ID</th>
                        <th>Course</th>
                        <th>Section</th>
                        <th>Status</th>
                        <th />
                      </tr>
                    </thead>
                    <tbody>
                      {filteredStudents.map((s) => (
                        <tr key={s.student_id}>
                          <td>
                            <button
                              className="student-cell"
                              onClick={() => openStudent(s)}
                            >
                              <div className="avatar student-avatar">
                                {s.first_name[0]}
                                {s.last_name[0]}
                              </div>
                              <strong>{fullname(s)}</strong>
                            </button>
                          </td>
                          <td className="mono">{s.student_id}</td>
                          <td>{s.course}</td>
                          <td>{s.section}</td>
                          <td>
                            <Badge value={s.status} />
                          </td>
                          <td>
                            <button
                              className="text-link"
                              onClick={() => openStudent(s)}
                            >
                              View records
                              <Icon name="arrow" size={15} />
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
                {!filteredStudents.length && (
                  <Empty detail="Try a different student name, ID, or course." />
                )}
                <div className="table-footer">
                  <span>
                    Showing {filteredStudents.length} of {seed.students.length}{" "}
                    sample students
                  </span>
                  <span>Page 1 of 1</span>
                </div>
              </section>
              <div className="sample-note">
                <Icon name="shield" size={15} />
                Student identity and profile data are owned by the Registrar
                System.
              </div>
            </>
          )}
          {page === "students" && selected && (
            <>
              <button
                className="back-link"
                onClick={() => {
                  setSelected(null)
                  setSearch("")
                }}
              >
                <span className="back-arrow">
                  <Icon name="arrow" size={16} />
                </span>
                Back to students
              </button>
              <div className="page-heading">
                <div>
                  <div className="eyebrow">STUDENT CARE</div>
                  <h1>Student health record</h1>
                  <p>A complete view of this student’s clinic-managed care.</p>
                </div>
              </div>
              <div className="panel student-profile">
                <div className="avatar large-avatar">
                  {selected.first_name[0]}
                  {selected.last_name[0]}
                </div>
                <div>
                  <h2>{fullname(selected)}</h2>
                  <p>
                    {selected.student_id}
                    <span>·</span>
                    {selected.course}
                    <span>·</span>Section {selected.section}
                  </p>
                </div>
                <Badge value={selected.status} />
                <span className="profile-source">
                  <Icon name="lock" size={14} />
                  Registrar profile
                </span>
              </div>
              <div className="tabs" role="tablist">
                {["Health record", "Consultations", "Health status"].map(
                  (t) => (
                    <button
                      role="tab"
                      aria-selected={tab === t}
                      className={tab === t ? "active" : ""}
                      key={t}
                      onClick={() => {
                        setTab(t)
                        setSearch("")
                      }}
                    >
                      <Icon
                        name={
                          t === "Health record"
                            ? "record"
                            : t === "Consultations"
                              ? "activity"
                              : "shield"
                        }
                        size={18}
                      />
                      {t}
                      <span>
                        {t === "Health record"
                          ? studentRecords.length
                          : t === "Consultations"
                            ? visits.filter(
                                (v) => v.student_id === selected.student_id,
                              ).length
                            : studentStatuses.length}
                      </span>
                    </button>
                  ),
                )}
              </div>
              <section className="panel record-panel">
                <div className="panel-heading">
                  <div>
                    <h2>
                      {tab === "Health record"
                        ? "Health information"
                        : tab === "Consultations"
                          ? "Consultation / clinic visits"
                          : "Health status history"}
                    </h2>
                    <p>
                      {tab === "Health record"
                        ? "Persistent health information and medical history."
                        : tab === "Consultations"
                          ? "Complaints, assessments, and treatment at each visit."
                          : "Clinic-issued health clearances and restrictions."}
                    </p>
                  </div>
                  <Button
                    icon="plus"
                    disabled={selected.status !== "ACTIVE"}
                    onClick={() =>
                      setEditor({
                        kind:
                          tab === "Health record"
                            ? "record"
                            : tab === "Consultations"
                              ? "consultation"
                              : "status",
                      })
                    }
                  >
                    {tab === "Health record"
                      ? "Create record"
                      : tab === "Consultations"
                        ? "New consultation"
                        : "Record status"}
                  </Button>
                </div>
                {selected.status !== "ACTIVE" && (
                  <div className="notice">
                    New clinic records can only be created for active students.
                  </div>
                )}
                {tab === "Health record" &&
                  (studentRecords.length ? (
                    studentRecords.map((r) => (
                      <article
                        className="record-article"
                        key={r.health_record_id}
                      >
                        <div className="record-meta">
                          <span>Health record #{r.health_record_id}</span>
                          <div className="row-actions">
                            <button
                              className="icon-button"
                              aria-label="Edit health record"
                              onClick={() =>
                                setEditor({ kind: "record", existing: r })
                              }
                            >
                              <Icon name="edit" size={17} />
                            </button>
                            <button
                              className="icon-button danger-icon"
                              aria-label="Delete health record"
                              onClick={() =>
                                deleteRecord("record", r.health_record_id)
                              }
                            >
                              <Icon name="trash" size={17} />
                            </button>
                          </div>
                        </div>
                        <div className="vitals-grid">
                          <div>
                            <span>Blood type</span>
                            <strong>{r.blood_type ?? "Not recorded"}</strong>
                          </div>
                          <div>
                            <span>Height</span>
                            <strong>
                              {r.height_cm ?? "—"} <small>cm</small>
                            </strong>
                          </div>
                          <div>
                            <span>Weight</span>
                            <strong>
                              {r.weight_kg ?? "—"} <small>kg</small>
                            </strong>
                          </div>
                        </div>
                        <dl className="record-details">
                          <div>
                            <dt>Allergies</dt>
                            <dd>{r.allergies || "Not recorded"}</dd>
                          </div>
                          <div>
                            <dt>Medical history</dt>
                            <dd>{r.medical_history || "Not recorded"}</dd>
                          </div>
                          <div>
                            <dt>Current medications</dt>
                            <dd>{r.current_medications || "Not recorded"}</dd>
                          </div>
                        </dl>
                        <div className="record-dates">
                          <span>Created {date(r.created_at)}</span>
                          <span>Updated {date(r.updated_at)}</span>
                        </div>
                      </article>
                    ))
                  ) : (
                    <Empty
                      text="No health records yet"
                      detail="Create a health record for this student to get started."
                    />
                  ))}
                {tab === "Consultations" && (
                  <>
                    <div className="record-search">
                      <Search
                        value={search}
                        onChange={setSearch}
                        placeholder="Search complaints, assessments, or notes..."
                      />
                    </div>
                    {studentVisits.length ? (
                      studentVisits.map((v) => (
                        <article
                          className="record-article"
                          key={v.consultation_id}
                        >
                          <div className="record-meta">
                            <div>
                              <Badge value="CONSULTATION" />
                              <span className="visit-date">
                                {date(v.consulted_at, true)} · #
                                {v.consultation_id}
                              </span>
                            </div>
                            <div className="row-actions">
                              <button
                                className="icon-button"
                                aria-label="Edit consultation"
                                onClick={() =>
                                  setEditor({
                                    kind: "consultation",
                                    existing: v,
                                  })
                                }
                              >
                                <Icon name="edit" size={17} />
                              </button>
                              <button
                                className="icon-button danger-icon"
                                aria-label="Delete consultation"
                                onClick={() =>
                                  deleteRecord(
                                    "consultation",
                                    v.consultation_id,
                                  )
                                }
                              >
                                <Icon name="trash" size={17} />
                              </button>
                            </div>
                          </div>
                          <h3 className="complaint">{v.chief_complaint}</h3>
                          <dl className="record-details">
                            <div>
                              <dt>Assessment</dt>
                              <dd>{v.assessment || "Not recorded"}</dd>
                            </div>
                            <div>
                              <dt>Treatment</dt>
                              <dd>{v.treatment || "Not recorded"}</dd>
                            </div>
                            <div>
                              <dt>Notes</dt>
                              <dd>{v.notes || "Not recorded"}</dd>
                            </div>
                          </dl>
                        </article>
                      ))
                    ) : (
                      <Empty
                        text="No consultations found"
                        detail={
                          search
                            ? "Try another complaint or assessment."
                            : "Record this student’s first clinic visit."
                        }
                      />
                    )}
                  </>
                )}
                {tab === "Health status" &&
                  (studentStatuses.length ? (
                    studentStatuses.map((s) => (
                      <article className="record-article" key={s.status_id}>
                        <div className="record-meta">
                          <Badge value={s.status} />
                          <div className="row-actions">
                            <button
                              className="icon-button"
                              aria-label="Edit health status"
                              onClick={() =>
                                setEditor({ kind: "status", existing: s })
                              }
                            >
                              <Icon name="edit" size={17} />
                            </button>
                            <button
                              className="icon-button danger-icon"
                              aria-label="Delete health status"
                              onClick={() =>
                                deleteRecord("status", s.status_id)
                              }
                            >
                              <Icon name="trash" size={17} />
                            </button>
                          </div>
                        </div>
                        <p className="status-remarks">
                          {s.remarks || "No remarks"}
                        </p>
                        <div className="record-dates">
                          <span>Status #{s.status_id}</span>
                          <span>Effective {date(s.effective_at, true)}</span>
                        </div>
                      </article>
                    ))
                  ) : (
                    <Empty
                      text="No health status available"
                      detail="Record a clearance, restriction, or observation status."
                    />
                  ))}
              </section>
              {tab === "Health status" && (
                <div className="notice integration-notice">
                  <Icon name="shield" />
                  <div>
                    <strong>Faculty & Student Portal integrations</strong>
                    <p>
                      The contract permits read-only access to the latest
                      status, remarks, and effective date only. Full health
                      records and consultations are not shared.
                    </p>
                  </div>
                </div>
              )}
            </>
          )}

          {page === "medicines" && (
            <>
              <div className="page-heading">
                <div>
                  <div className="eyebrow">MEDICINE INVENTORY</div>
                  <h1>Medicine stock</h1>
                  <p>
                    Check medicine availability and monitor low-stock items.
                  </p>
                </div>
                <Button
                  variant="secondary"
                  icon="refresh"
                  onClick={() =>
                    setInfo(
                      "This preview uses the medicine examples in your API contract. A live Inventory integration is not connected, so refreshing cannot request updated stock.",
                    )
                  }
                >
                  Request stock information
                </Button>
              </div>
              <div className="medicine-summary">
                <div>
                  <div className="stat-icon">
                    <Icon name="pill" />
                  </div>
                  <span>
                    Total stock
                    <strong>
                      {seed.medicines.reduce(
                        (n, m) => n + m.quantity_in_stock,
                        0,
                      )}{" "}
                      <small>tablets</small>
                    </strong>
                  </span>
                </div>
                <div>
                  <div className="stat-icon">
                    <Icon name="check" />
                  </div>
                  <span>
                    Available medicines
                    <strong>
                      {
                        seed.medicines.filter((m) => m.quantity_in_stock > 0)
                          .length
                      }
                    </strong>
                  </span>
                </div>
                <div>
                  <div className="stat-icon amber-icon">
                    <Icon name="alert" />
                  </div>
                  <span>
                    Low-stock medicines<strong>{lowStock.length}</strong>
                  </span>
                </div>
              </div>
              <section className="panel">
                <div className="table-toolbar">
                  <Search
                    value={search}
                    onChange={setSearch}
                    placeholder="Search medicine name or ID..."
                  />
                  <div className="segmented">
                    {["All", "Available", "Low stock"].map((f) => (
                      <button
                        key={f}
                        className={filter === f ? "active" : ""}
                        onClick={() => setFilter(f)}
                      >
                        {f}
                      </button>
                    ))}
                  </div>
                </div>
                <div className="table-scroll">
                  <table>
                    <thead>
                      <tr>
                        <th>Medicine</th>
                        <th>Medicine ID</th>
                        <th>Stock quantity</th>
                        <th>Reorder level</th>
                        <th>Availability</th>
                        <th />
                      </tr>
                    </thead>
                    <tbody>
                      {filteredMedicines.map((m) => (
                        <tr key={m.medicine_id}>
                          <td>
                            <button
                              className="student-cell"
                              onClick={() => setMedicine(m)}
                            >
                              <div className="medicine-icon">
                                <Icon name="pill" size={20} />
                              </div>
                              <div className="table-name">
                                <strong>{m.name}</strong>
                                <span>{m.generic_name}</span>
                              </div>
                            </button>
                          </td>
                          <td className="mono">{m.medicine_id}</td>
                          <td>
                            <strong>{m.quantity_in_stock}</strong>{" "}
                            <span className="muted-text">{m.unit}s</span>
                          </td>
                          <td>{m.reorder_level}</td>
                          <td>
                            <Badge
                              value={
                                m.quantity_in_stock === 0
                                  ? "Out of stock"
                                  : m.is_low_stock
                                    ? "Low stock"
                                    : "Available"
                              }
                            />
                          </td>
                          <td>
                            <button
                              className="icon-button"
                              aria-label={`View ${m.name}`}
                              onClick={() => setMedicine(m)}
                            >
                              <Icon name="chevron" size={18} />
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
                {!filteredMedicines.length && (
                  <Empty
                    text="No medicines found"
                    detail="Try a different medicine name or filter."
                  />
                )}
                <div className="table-footer">
                  <span>
                    Showing {filteredMedicines.length} of{" "}
                    {seed.medicines.length} example medicines
                  </span>
                  <span>Inventory · Read-only</span>
                </div>
              </section>
              <div className="sample-note">
                <Icon name="lock" size={15} />
                Medicine catalog and stock belong to Inventory. Low stock means
                quantity is at or below the reorder level.
              </div>
            </>
          )}
          {page === "settings" && (
            <>
              <div className="page-heading">
                <div>
                  <div className="eyebrow">YOUR ACCOUNT</div>
                  <h1>Settings</h1>
                  <p>Account information and sign-in preferences.</p>
                </div>
              </div>
              <div className="settings-layout">
                <section className="panel">
                  <div className="panel-heading">
                    <div>
                      <h2>Account information</h2>
                      <p>Current user example from /api/auth/me/.</p>
                    </div>
                    <Icon name="students" />
                  </div>
                  <dl className="record-details settings-details">
                    <div>
                      <dt>User ID</dt>
                      <dd>1</dd>
                    </div>
                    <div>
                      <dt>Username</dt>
                      <dd>clinic_staff</dd>
                    </div>
                    <div>
                      <dt>Email</dt>
                      <dd>clinic@example.com</dd>
                    </div>
                    <div>
                      <dt>is_staff</dt>
                      <dd>false</dd>
                    </div>
                  </dl>
                  <div className="panel-foot">
                    Demo account · No live authenticated session
                  </div>
                </section>
                <section className="panel">
                  <div className="panel-heading">
                    <div>
                      <h2>Sign-in & security</h2>
                      <p>Manage your account credentials.</p>
                    </div>
                    <Icon name="lock" />
                  </div>
                  <div className="settings-option">
                    <div>
                      <h3>Change username</h3>
                      <p>Update your clinic sign-in username.</p>
                    </div>
                    <Button variant="secondary" disabled>
                      Not available
                    </Button>
                  </div>
                  <div className="settings-option">
                    <div>
                      <h3>Change password</h3>
                      <p>Update your account password.</p>
                    </div>
                    <Button variant="secondary" disabled>
                      Not available
                    </Button>
                  </div>
                  <div className="notice">
                    Username and password change endpoints are not defined in
                    the supplied API contract. These actions are unavailable in
                    this preview.
                  </div>
                </section>
              </div>
            </>
          )}
          {page === "admin" && (
            <>
              <div className="page-heading">
                <div>
                  <div className="eyebrow">CLINIC MANAGEMENT</div>
                  <h1>Administration</h1>
                  <p>Manage clinic staff profiles and account access.</p>
                </div>
                <Button icon="plus" onClick={() => setEditor({ kind: "user" })}>
                  Add staff account
                </Button>
              </div>
              <div className="notice admin-notice">
                <Icon name="shield" size={18} />
                <span>
                  Administrator-only operations are shown for demonstration. No
                  live permissions are granted.
                </span>
              </div>
              <section className="panel">
                <div className="table-toolbar">
                  <Search
                    value={search}
                    onChange={setSearch}
                    placeholder="Search staff name, username, or email..."
                  />
                  <span className="muted-text">
                    {users.length} staff{" "}
                    {users.length === 1 ? "account" : "accounts"}
                  </span>
                </div>
                <div className="table-scroll">
                  <table>
                    <thead>
                      <tr>
                        <th>Staff member</th>
                        <th>Username</th>
                        <th>Role</th>
                        <th>Status</th>
                        <th>Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {filteredUsers.map((u) => (
                        <tr key={u.user_id}>
                          <td>
                            <div className="student-cell">
                              <div className="avatar student-avatar">
                                {u.first_name[0] ?? "C"}
                                {u.last_name[0] ?? "S"}
                              </div>
                              <div className="table-name">
                                <strong>
                                  {u.first_name} {u.last_name}
                                </strong>
                                <span>{u.email || "No email provided"}</span>
                              </div>
                            </div>
                          </td>
                          <td>{u.username}</td>
                          <td>{u.role ?? "Not assigned"}</td>
                          <td>
                            <Badge
                              value={u.is_active ? "ACTIVE" : "INACTIVE"}
                            />
                          </td>
                          <td>
                            <div className="row-actions">
                              <button
                                className="text-link"
                                onClick={() =>
                                  setEditor({ kind: "user", existing: u })
                                }
                              >
                                <Icon name="edit" size={15} />
                                Edit
                              </button>
                              <button
                                className={`text-link ${
                                  u.is_active ? "danger-link" : ""
                                }`}
                                onClick={() =>
                                  setConfirmation({
                                    title: `${
                                      u.is_active ? "Deactivate" : "Activate"
                                    } ${u.username}?`,
                                    action: () => {
                                      setUsers(
                                        users.map((x) =>
                                          x.user_id === u.user_id
                                            ? { ...x, is_active: !x.is_active }
                                            : x,
                                        ),
                                      )
                                      setToast(
                                        `Account ${
                                          u.is_active
                                            ? "deactivated"
                                            : "activated"
                                        } in the demo workspace.`,
                                      )
                                    },
                                  })
                                }
                              >
                                {u.is_active ? "Deactivate" : "Activate"}
                              </button>
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
                {!filteredUsers.length && (
                  <Empty
                    text="No staff accounts found"
                    detail="Try a different staff name, username, or email."
                  />
                )}
                <div className="table-footer">
                  <span>
                    {filteredUsers.length}{" "}
                    {filteredUsers.length === 1 ? "account" : "accounts"}
                  </span>
                  <span>Page 1 of 1</span>
                </div>
              </section>
              <div className="sample-note">
                <Icon name="lock" size={15} />
                The contract supports activation and deactivation, not user
                deletion or password changes.
              </div>
            </>
          )}
          <footer className="app-footer">
            <span>IDSC Clinic System</span>
            <span>Thoughtful care. Connected information.</span>
          </footer>
        </main>
      </div>
      {toast && (
        <div className="toast" role="status">
          <Icon name="check" size={18} />
          {toast}
          <button
            className="icon-button"
            onClick={() => setToast("")}
            aria-label="Dismiss message"
          >
            <Icon name="close" size={16} />
          </button>
        </div>
      )}
      {editor && (
        <Modal
          title={`${editor.existing ? "Edit" : "Create"} ${
            editor.kind === "record"
              ? "health record"
              : editor.kind === "status"
                ? "health status"
                : editor.kind === "user"
                  ? "staff account"
                  : "consultation"
          }`}
          onClose={() => setEditor(null)}
        >
          <form onSubmit={saveEditor}>
            <div className="modal-content">
              <div className="notice compact">
                Demo only. Changes stay in memory and reset when the page
                reloads.
              </div>
              {editor.kind !== "user" && (
                <div className="editor-student">
                  <Icon name="students" size={18} />
                  <strong>{selected && fullname(selected)}</strong>
                  <span>{selected?.student_id}</span>
                </div>
              )}
              {editor.kind === "record" &&
                (() => {
                  const r = editor.existing as HealthRecord | undefined
                  return (
                    <>
                      <Field
                        label="Blood type"
                        name="blood_type"
                        value={r?.blood_type ?? "Unknown"}
                        options={[
                          "A+",
                          "A-",
                          "B+",
                          "B-",
                          "AB+",
                          "AB-",
                          "O+",
                          "O-",
                          "Unknown",
                        ]}
                      />
                      <div className="form-grid">
                        <Field
                          label="Height (cm)"
                          name="height_cm"
                          type="number"
                          value={r?.height_cm}
                          min={0.01}
                          max={300}
                        />
                        <Field
                          label="Weight (kg)"
                          name="weight_kg"
                          type="number"
                          value={r?.weight_kg}
                          min={0.01}
                          max={500}
                        />
                      </div>
                      <Field
                        label="Allergies"
                        name="allergies"
                        value={r?.allergies}
                        multiline
                      />
                      <Field
                        label="Medical history"
                        name="medical_history"
                        value={r?.medical_history}
                        multiline
                      />
                      <Field
                        label="Current medications"
                        name="current_medications"
                        value={r?.current_medications}
                        multiline
                      />
                    </>
                  )
                })()}
              {editor.kind === "consultation" &&
                (() => {
                  const v = editor.existing as Consultation | undefined
                  return (
                    <>
                      <Field
                        label="Chief complaint"
                        name="chief_complaint"
                        value={v?.chief_complaint}
                        required
                        multiline
                      />
                      <Field
                        label="Assessment"
                        name="assessment"
                        value={v?.assessment}
                        multiline
                      />
                      <Field
                        label="Treatment"
                        name="treatment"
                        value={v?.treatment}
                        multiline
                      />
                      <Field
                        label="Notes"
                        name="notes"
                        value={v?.notes}
                        multiline
                      />
                    </>
                  )
                })()}
              {editor.kind === "status" &&
                (() => {
                  const s = editor.existing as HealthStatus | undefined
                  return (
                    <>
                      <Field
                        label="Status"
                        name="status"
                        value={s?.status}
                        options={["CLEARED", "RESTRICTED", "UNDER_OBSERVATION"]}
                        required
                      />
                      <Field
                        label="Remarks"
                        name="remarks"
                        value={s?.remarks}
                        multiline
                      />
                    </>
                  )
                })()}
              {editor.kind === "user" &&
                (() => {
                  const u = editor.existing as ClinicUser | undefined
                  return (
                    <>
                      {!u ? (
                        <Field label="Username" name="username" required />
                      ) : (
                        <div className="editor-student">
                          <strong>{u.username}</strong>
                          <span>User #{u.user_id}</span>
                        </div>
                      )}
                      <div className="form-grid">
                        <Field
                          label="First name"
                          name="first_name"
                          value={u?.first_name}
                        />
                        <Field
                          label="Last name"
                          name="last_name"
                          value={u?.last_name}
                        />
                      </div>
                      <Field
                        label="Email"
                        name="email"
                        type="email"
                        value={u?.email}
                      />
                      {!u && (
                        <>
                          <Field
                            label="Temporary password"
                            name="password"
                            type="password"
                            required
                          />
                          <small className="muted-text">
                            The password is not stored or used for
                            authentication in this demo.
                          </small>
                        </>
                      )}
                    </>
                  )
                })()}
            </div>
            <div className="modal-actions">
              <Button variant="secondary" onClick={() => setEditor(null)}>
                Cancel
              </Button>
              <Button type="submit" icon="check">
                {editor.existing ? "Save changes" : "Create"}
              </Button>
            </div>
          </form>
        </Modal>
      )}
      {confirmation && (
        <Modal title={confirmation.title} onClose={() => setConfirmation(null)}>
          <div className="modal-content">
            <p>
              This changes the demo workspace only.
              {confirmation.title.startsWith("Delete")
                ? " This action cannot be undone."
                : ""}
            </p>
          </div>
          <div className="modal-actions">
            <Button variant="secondary" onClick={() => setConfirmation(null)}>
              Cancel
            </Button>
            <Button
              variant="danger"
              onClick={() => {
                confirmation.action()
                setConfirmation(null)
              }}
            >
              Confirm
            </Button>
          </div>
        </Modal>
      )}
      {medicine && (
        <Modal title={medicine.name} onClose={() => setMedicine(null)}>
          <div className="modal-content">
            <span className="integration-chip">
              <Icon name="lock" size={14} />
              Inventory · Read-only
            </span>
            <dl className="record-details medicine-details">
              <div>
                <dt>Medicine ID</dt>
                <dd>{medicine.medicine_id}</dd>
              </div>
              <div>
                <dt>Generic name</dt>
                <dd>{medicine.generic_name}</dd>
              </div>
              <div>
                <dt>Unit</dt>
                <dd>{medicine.unit}</dd>
              </div>
              <div>
                <dt>Quantity in stock</dt>
                <dd>{medicine.quantity_in_stock}</dd>
              </div>
              <div>
                <dt>Reorder level</dt>
                <dd>{medicine.reorder_level}</dd>
              </div>
              <div>
                <dt>Low stock</dt>
                <dd>{String(medicine.is_low_stock)}</dd>
              </div>
              <div>
                <dt>Status</dt>
                <dd>
                  <Badge value={medicine.status} />
                </dd>
              </div>
            </dl>
          </div>
          <div className="modal-actions">
            <Button variant="secondary" onClick={() => setMedicine(null)}>
              Close
            </Button>
          </div>
        </Modal>
      )}
      {info && (
        <Modal title="Inventory integration" onClose={() => setInfo("")}>
          <div className="modal-content">
            <p>{info}</p>
          </div>
          <div className="modal-actions">
            <Button variant="secondary" onClick={() => setInfo("")}>
              Close
            </Button>
          </div>
        </Modal>
      )}
    </div>
  )
}
