# 📘 Student Record Management System

> A multi-layered academic record system built with **MySQL**, **C data structures**, and a **Python CLI** — developed across six structured phases.

---

## Technology Stack

| Layer | Technology | Purpose |
|---|---|---|
| Database | MySQL 8.0+ | Relational storage, triggers, views |
| Data Structures | C (GCC) | In-memory algorithms & benchmarking |
| Backend | Python 3.10+ | Models, controllers, services |
| CLI | Python (built-in) | Menu-driven terminal interface |
| Testing | pytest | Unit + integration tests |

---

## Quick Start

### Prerequisites

- Python 3.10+
- MySQL 8.0+ (or MariaDB 10.6+)

### 1 — Install dependencies

```powershell
pip install -r requirements.txt
```

### 2 — Set up the database

```powershell
mysql -u root -p < database/setup.sql
```

### 3 — Configure credentials

```powershell
# Windows PowerShell (session)
$env:DB_PASSWORD = "your_password"

# Or create a .env file (permanent)
Copy-Item .env.example .env
# Edit .env and set DB_PASSWORD
```

### 4 — Launch

```powershell
python main.py
# or
.\run.bat
```

---

## Project Structure

```
Student Record Management System/
│
├── database/                    # Phase 1 — MySQL schema & seed data
│   ├── schema.sql
│   ├── stored_procedures.sql
│   ├── sample_data.sql
│   └── setup.sql
│
├── c_modules/                   # Phase 2 — C data structures
│   ├── linked_list.{h,c}        # Doubly linked list
│   ├── bst.{h,c}                # Binary search tree
│   ├── hash_table.{h,c}         # Hash table (separate chaining)
│   ├── sorting.{h,c}            # Bubble/Selection/Insertion/Merge/Quick sort
│   ├── searching.{h,c}          # Linear & binary search
│   ├── file_ops.{h,c}           # Binary & CSV file I/O
│   ├── main.c                   # Full test harness
│   └── Makefile
│
├── student_management/          # Phase 3+4 — Python backend + CLI
│   ├── config/database.py       # DB connection & session helpers
│   ├── models/                  # Student, Course, Enrollment, Attendance
│   ├── controllers/             # CRUD controllers for each entity
│   ├── services/report_service.py
│   ├── cli/                     # Menu-driven TUI (5 sub-menus, 44 ops)
│   └── utils/                   # Logger, validators, helpers
│
├── tests/                       # Phase 5 — pytest (205 tests)
│   ├── conftest.py
│   ├── unit/                    # 117 tests — no DB required
│   └── integration/             # 88 tests — requires live DB
│
├── docs/                        # Phase 6 — Documentation
│   ├── USER_GUIDE.md
│   ├── DEVELOPER_GUIDE.md
│   └── API_REFERENCE.md
│
├── main.py                      # Entry point
├── run.bat                      # Windows launcher
├── pyproject.toml               # Packaging metadata
├── pytest.ini
├── requirements.txt
└── .env.example
```

---

## CLI Menu Map

```
Main Menu
├── [1] 👤  Student Management
│         List · Search · Detail · Add · Update · Status · Toppers · Stats
├── [2] 📚  Course Management
│         List · Search · Detail · Enrolled students · Summary · Add · Update · Deactivate
├── [3] 📋  Enrollment & Marks
│         Enroll · View (student/course) · Marks (single/bulk) · Drop
│         Grade distribution bar chart · Full CGPA transcript
├── [4] 📅  Attendance Management
│         Mark (single/bulk class) · View by date · Student history
│         Course summary · Student summary · Defaulters · Class dates
└── [5] 📊  Reports & Analytics
          System dashboard · Department stats · Top performers
          Transcript (console + CSV export) · Grade distribution · Defaulters
```

---

## Database Schema

| Table | Purpose |
|---|---|
| `departments` | Academic departments |
| `students` | Student master data (GPA auto-computed) |
| `faculty` | Faculty members |
| `courses` | Course catalogue |
| `enrollments` | Student-course mapping with marks & grades |
| `attendance` | Daily attendance records |
| `users` | Login accounts |
| `audit_log` | Change tracking |

**Automated behaviours via triggers:**
- `student_code` auto-generated as `STU{YEAR}{NNNN}` on insert
- `grade` / `grade_points` computed from marks automatically
- `gpa` recalculated after every marks update

**Views:** `vw_student_full_info` · `vw_course_enrollment_summary` · `vw_attendance_summary`

---

## C Data Structures

| Module | Structure | Avg. Complexity |
|---|---|---|
| `linked_list` | Doubly Linked List | Search O(n) |
| `bst` | Binary Search Tree | Search O(log n) |
| `hash_table` | Hash Table (Knuth hash) | Search O(1) |
| `sorting` | Merge / Quick sort | O(n log n) |

```powershell
cd c_modules
make run       # build + run all tests
```

---

## Testing

```powershell
# All 205 tests
$env:DB_PASSWORD = "your_password"
python -m pytest tests/

# Unit tests only (no DB)
python -m pytest tests/unit/ -m unit

# Integration tests only
python -m pytest tests/integration/ -m integration

# With coverage
python -m pytest tests/ --cov=student_management --cov-report=html
```

| Test File | Tests | Needs DB |
|---|---|---|
| `unit/test_validators.py` | 73 | ✗ |
| `unit/test_models.py` | 44 | ✗ |
| `integration/test_student_controller.py` | 28 | ✓ |
| `integration/test_course_controller.py` | 21 | ✓ |
| `integration/test_enrollment_controller.py` | 22 | ✓ |
| `integration/test_attendance_controller.py` | 19 | ✓ |
| **Total** | **207** | — |

---

## Documentation

| Document | Description |
|---|---|
| [USER_GUIDE.md](docs/USER_GUIDE.md) | Step-by-step usage guide for every menu |
| [DEVELOPER_GUIDE.md](docs/DEVELOPER_GUIDE.md) | Architecture, patterns, testing, extending the system |
| [API_REFERENCE.md](docs/API_REFERENCE.md) | Full API for all models, controllers, services, and utilities |
