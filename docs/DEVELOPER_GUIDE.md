# Developer Guide — Student Record Management System

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Project Structure](#2-project-structure)
3. [Development Environment Setup](#3-development-environment-setup)
4. [Database Layer](#4-database-layer)
5. [C Modules Layer](#5-c-modules-layer)
6. [Python Backend Layer](#6-python-backend-layer)
7. [CLI Layer](#7-cli-layer)
8. [Testing](#8-testing)
9. [Adding New Features](#9-adding-new-features)
10. [Known Limitations](#10-known-limitations)

---

## 1. Architecture Overview

The system is organised into four independent layers that communicate through well-defined interfaces:

```
┌─────────────────────────────────────────────────┐
│              CLI Layer (Phase 4)                 │
│   student_management/cli/  — menu-driven TUI    │
└────────────────────┬────────────────────────────┘
                     │ calls
┌────────────────────▼────────────────────────────┐
│           Python Backend (Phase 3)              │
│  controllers/ · services/ · models/ · utils/   │
└────────────────────┬────────────────────────────┘
                     │ SQL via connector
┌────────────────────▼────────────────────────────┐
│              MySQL Database (Phase 1)            │
│  schema · stored procedures · triggers · views  │
└─────────────────────────────────────────────────┘

  C Modules (Phase 2) — standalone in-memory layer
  c_modules/ — linked list, BST, hash table,
                sorting, searching, file I/O
```

### Design Decisions

| Decision | Rationale |
|---|---|
| Python dataclasses for models | Lightweight, type-hinted, no ORM overhead |
| `from_row()` factory methods | Decouples DB schema from domain objects |
| Context manager for DB sessions | Guarantees commit/rollback without boilerplate |
| Soft-delete for students | Preserves referential integrity for historical records |
| DB triggers for grades/GPA | Keeps business rules at the data layer |
| Separate unit/integration marks | Allows offline development without a live DB |

---

## 2. Project Structure

```
Student Record Management System/
│
├── database/                    # Phase 1 — MySQL
│   ├── schema.sql               # DDL: tables, indexes, triggers, views
│   ├── stored_procedures.sql    # Stored procedures
│   ├── sample_data.sql          # Seed data for development
│   └── setup.sql                # Master script: sources all three above
│
├── c_modules/                   # Phase 2 — C data structures
│   ├── student.h                # Shared Student struct
│   ├── linked_list.{h,c}
│   ├── bst.{h,c}
│   ├── hash_table.{h,c}
│   ├── sorting.{h,c}
│   ├── searching.{h,c}
│   ├── file_ops.{h,c}
│   ├── main.c                   # Test harness
│   └── Makefile
│
├── student_management/          # Phase 3+4 — Python
│   ├── config/
│   │   └── database.py          # DB connection, context manager, execute_*
│   ├── models/
│   │   ├── student.py
│   │   ├── course.py
│   │   ├── enrollment.py        # Also has compute_grade()
│   │   └── attendance.py        # Also has AttendanceSummary
│   ├── controllers/
│   │   ├── student_controller.py
│   │   ├── course_controller.py
│   │   ├── enrollment_controller.py
│   │   └── attendance_controller.py
│   ├── services/
│   │   └── report_service.py    # Console + CSV reports
│   ├── cli/
│   │   ├── base_menu.py         # BaseMenu + MenuItem engine
│   │   ├── main_menu.py
│   │   ├── student_menu.py
│   │   ├── course_menu.py
│   │   ├── enrollment_menu.py
│   │   ├── attendance_menu.py
│   │   └── reports_menu.py
│   └── utils/
│       ├── logger.py
│       ├── validators.py
│       └── helpers.py
│
├── tests/                       # Phase 5 — pytest
│   ├── conftest.py              # Fixtures (unit + DB-backed)
│   ├── unit/
│   │   ├── test_validators.py
│   │   └── test_models.py
│   └── integration/
│       ├── test_student_controller.py
│       ├── test_course_controller.py
│       ├── test_enrollment_controller.py
│       └── test_attendance_controller.py
│
├── docs/                        # Phase 6 — Documentation
│   ├── USER_GUIDE.md
│   ├── DEVELOPER_GUIDE.md       # (this file)
│   └── API_REFERENCE.md
│
├── logs/                        # Auto-created: srms.log (rotating, 5 MB)
├── reports/                     # Auto-created: exported CSVs
│
├── main.py                      # Application entry point
├── pyproject.toml               # Packaging + tool config
├── pytest.ini                   # pytest config
├── requirements.txt             # Pip install targets
├── run.bat                      # Windows launcher
├── .env.example                 # Environment variable template
└── .gitignore
```

---

## 3. Development Environment Setup

```powershell
# 1. Clone / open the project
cd "d:\Projects\Student Record Management System"

# 2. Create a virtual environment (recommended)
python -m venv .venv
.venv\Scripts\Activate.ps1

# 3. Install all dependencies including dev extras
pip install -e ".[all]"
# or without packaging:
pip install -r requirements.txt

# 4. Set up the database
mysql -u root -p < database/setup.sql

# 5. Configure credentials
Copy-Item .env.example .env
# Edit .env and set DB_PASSWORD

# 6. Verify setup
python -m pytest tests/unit/    # no DB needed
$env:DB_PASSWORD="your_pw"
python -m pytest tests/         # full suite
```

---

## 4. Database Layer

### Connection Management (`student_management/config/database.py`)

```python
from student_management.config.database import (
    db_session,        # context manager for transactional writes
    execute_query,     # SELECT → list[dict]
    execute_non_query, # INSERT/UPDATE/DELETE → affected rows
)

# Read example
rows = execute_query("SELECT * FROM students WHERE status = %s", ("active",))

# Write example
with db_session() as cur:
    cur.execute("INSERT INTO ...", (...))
    new_id = cur.lastrowid         # auto-commit on context exit
```

### Environment Variables

| Variable | Default | Description |
|---|---|---|
| `DB_HOST` | `localhost` | MySQL hostname |
| `DB_PORT` | `3306` | MySQL port |
| `DB_NAME` | `student_management_db` | Database name |
| `DB_USER` | `root` | MySQL username |
| `DB_PASSWORD` | *(required)* | MySQL password |

### Schema Highlights

- **Triggers:** `trg_student_code` (auto-generates `STU{YEAR}{NNNN}`), `trg_grade_after_marks` (computes grade/grade_points from total marks), `trg_gpa_after_marks` (recalculates student GPA)
- **Views:** `vw_student_full_info`, `vw_course_enrollment_summary`, `vw_attendance_summary`
- **All foreign keys** are declared with `ON DELETE RESTRICT` to prevent orphaned records

---

## 5. C Modules Layer

The C layer is a standalone set of in-memory data structure implementations.

### Build & Test

```powershell
cd c_modules
make        # compiles srms_test.exe
make run    # builds then runs all tests
make clean  # removes object files and binary
```

### Module Summary

| File | Structure | Key Operations |
|---|---|---|
| `linked_list.c` | Doubly Linked List | `ll_insert_sorted`, `ll_search_by_id`, `ll_delete_by_id`, `ll_traverse_reverse` |
| `bst.c` | Binary Search Tree | `bst_insert`, `bst_search`, `bst_delete`, `bst_inorder`, `bst_range_search` |
| `hash_table.c` | Hash Table | `ht_insert`, `ht_search`, `ht_delete`, `ht_load_factor` |
| `sorting.c` | 5 sort algorithms | `merge_sort`, `quick_sort`, `sort_benchmark` |
| `searching.c` | Linear + Binary search | `linear_search_by_name`, `binary_search_by_gpa` |
| `file_ops.c` | File I/O | `save_binary`, `load_binary`, `save_csv`, `load_csv`, `backup_file` |

---

## 6. Python Backend Layer

### Models (`student_management/models/`)

All models follow the same pattern:

```python
@dataclass
class Student:
    student_id: Optional[int] = None
    ...

    @classmethod
    def from_row(cls, row: dict) -> "Student":
        """Construct from a DB cursor row dict."""

    def to_dict(self) -> dict:
        """JSON-serialisable representation."""

    @property
    def full_name(self) -> str: ...    # computed property
```

### Controllers (`student_management/controllers/`)

All controllers are **stateless classes** with `@staticmethod` methods:

```python
from student_management.controllers import StudentController

students = StudentController.get_all(status="active")
student  = StudentController.add(first_name="Jane", ...)
ok       = StudentController.update(student_id=1, phone="0987654321")
```

### Validators (`student_management/utils/validators.py`)

All validators return `(bool, str)` — success flag + error message:

```python
from student_management.utils.validators import validate_student, validate_marks

ok, msg = validate_student({"first_name": "Jane", "email": "jane@example.com", ...})
if not ok:
    print(f"Validation error: {msg}")
```

### Logging (`student_management/utils/logger.py`)

```python
from student_management.utils.logger import setup_logger

log = setup_logger("my_module")
log.info("Something happened")    # also written to logs/srms.log
```

---

## 7. CLI Layer

### Adding a New Sub-menu

1. Create `student_management/cli/my_menu.py`:

```python
from .base_menu import BaseMenu, MenuItem

class MyMenu(BaseMenu):
    title = "My Feature"

    def __init__(self):
        super().__init__()
        self.items = [
            MenuItem("1", "Do something", self._do_something),
            MenuItem("0", "← Back",       self._go_back),
        ]

    def _do_something(self) -> None:
        print("Hello!")
        self._pause()
```

2. Register in `main_menu.py`:

```python
from .my_menu import MyMenu
...
MenuItem("6", "🔧  My Feature", MyMenu().run),
```

### BaseMenu Utilities

| Method | Description |
|---|---|
| `self._pause()` | Prints "Press Enter to continue..." |
| `self._go_back()` | Exits the current menu loop |
| `self._exit()` | Terminates the application |
| `self._get_student_id()` | Prompts and validates an integer student ID |
| `self._get_course_id()` | Prompts and validates an integer course ID |

---

## 8. Testing

### Running Tests

```powershell
# All tests
python -m pytest tests/

# Unit only (no DB)
python -m pytest tests/unit/ -m unit

# Integration only
python -m pytest tests/integration/ -m integration

# With coverage report
python -m pytest tests/ --cov=student_management --cov-report=html
# → open htmlcov/index.html
```

### Writing New Tests

**Unit test** — no fixtures needed:
```python
import pytest
from student_management.utils.validators import validate_email

@pytest.mark.unit
def test_valid_email():
    ok, _ = validate_email("user@example.com")
    assert ok is True
```

**Integration test** — use shared fixtures from `conftest.py`:
```python
import pytest

pytestmark = pytest.mark.integration

class TestMyFeature:
    def test_something(self, test_student):
        # test_student is auto-created and auto-cleaned up
        assert test_student.student_id is not None
```

### Fixture Reference

| Fixture | Scope | Description |
|---|---|---|
| `valid_student_dict` | function | Plain dict for validator tests |
| `student_row` | function | Mock DB row for `Student.from_row()` |
| `course_row` | function | Mock DB row for `Course.from_row()` |
| `enrollment_row` | function | Mock DB row for `Enrollment.from_row()` |
| `attendance_row` | function | Mock DB row for `Attendance.from_row()` |
| `db_available` | session | `True` if DB connection works |
| `require_db` | function | Skip test if DB unavailable |
| `cs_dept_id` | session | Department ID for CS from seed data |
| `test_student` | function | Creates + auto-deletes a student in DB |
| `test_course` | function | Creates + auto-deletes a course in DB |
| `test_enrollment` | function | Creates + auto-deletes an enrollment in DB |

---

## 9. Adding New Features

### Checklist for a new entity (e.g., Faculty)

- [ ] **Database:** Add table in `schema.sql`, seed in `sample_data.sql`
- [ ] **Model:** `student_management/models/faculty.py` with `from_row()` + `to_dict()`
- [ ] **Controller:** `student_management/controllers/faculty_controller.py`
- [ ] **CLI:** `student_management/cli/faculty_menu.py` extending `BaseMenu`
- [ ] **Register:** Add to `MainMenu` in `main_menu.py`
- [ ] **Tests:** `tests/unit/test_faculty_model.py` + `tests/integration/test_faculty_controller.py`
- [ ] **Docs:** Update `API_REFERENCE.md` and `USER_GUIDE.md`

---

## 10. Known Limitations

| Limitation | Notes |
|---|---|
| `avg_gp` column precision | DB GPA trigger can overflow on brand-new single-enrollment students if marks are updated multiple times in quick succession. Workaround: use a single marks update or ensure the schema uses `DECIMAL(5,2)` for `avg_gp`. |
| No authentication | The CLI does not implement user login. All users have full access. Phase 5+ could add `bcrypt`-based auth using the `users` table. |
| No multi-user support | The CLI is single-user; concurrent access is not handled at the application layer (MySQL handles it at the DB layer). |
| C modules are standalone | The C layer is not integrated into the Python layer yet. Integration via `ctypes` is a planned enhancement. |
| Reports are text/CSV only | PDF export requires `reportlab` and is not yet implemented. |
