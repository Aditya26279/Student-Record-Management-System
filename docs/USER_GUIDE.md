# User Guide — Student Record Management System

## Table of Contents

1. [Getting Started](#1-getting-started)
2. [Launching the Application](#2-launching-the-application)
3. [Main Menu Overview](#3-main-menu-overview)
4. [Student Management](#4-student-management)
5. [Course Management](#5-course-management)
6. [Enrollment & Marks](#6-enrollment--marks)
7. [Attendance Management](#7-attendance-management)
8. [Reports & Analytics](#8-reports--analytics)
9. [Tips & Keyboard Shortcuts](#9-tips--keyboard-shortcuts)
10. [Troubleshooting](#10-troubleshooting)

---

## 1. Getting Started

### Prerequisites

| Component | Minimum Version |
|---|---|
| Python | 3.10+ |
| MySQL / MariaDB | 8.0+ / 10.6+ |
| GCC (optional — C modules) | Any recent version |

### First-Time Setup

**Step 1 — Install Python dependencies:**
```powershell
pip install -r requirements.txt
```

**Step 2 — Set up the database:**
```powershell
mysql -u root -p < database/setup.sql
```

**Step 3 — Configure your credentials:**

Copy `.env.example` to `.env` and fill in your password:
```
DB_HOST=localhost
DB_PORT=3306
DB_NAME=student_management_db
DB_USER=root
DB_PASSWORD=your_password
```

Or set directly in PowerShell for the session:
```powershell
$env:DB_PASSWORD = "your_password"
```

---

## 2. Launching the Application

```powershell
# Option A — Direct (requires DB_PASSWORD in env)
python main.py

# Option B — Using the launcher script (reads .env automatically)
.\run.bat

# Option C — Offline/demo mode (no DB needed for navigation)
python main.py   # then choose 'y' when prompted
```

You will see the startup banner with a live DB connectivity check:

```
  ╔══════════════════════════════════════════════════════════╗
  ║     📘  Student Record Management System  📘            ║
  ╚══════════════════════════════════════════════════════════╝

  Version : 1.0.0
  DB      : student_management_db@localhost

  Connecting to database... OK
```

---

## 3. Main Menu Overview

```
  [1]  👤  Student Management
  [2]  📚  Course Management
  [3]  📋  Enrollment & Marks
  [4]  📅  Attendance Management
  [5]  📊  Reports & Analytics
  [0]  🚪  Exit
```

Type a number and press **Enter** to select an option.  
Type **0** in any sub-menu to go back to the previous menu.

---

## 4. Student Management

Access via **Main Menu → [1]**

| Option | Description |
|---|---|
| **[1] List all students** | Show all students, with optional status filter (active / graduated / inactive / all) |
| **[2] Search students** | Full-text search across name, email, and student code |
| **[3] View student details** | Enter a Student ID to see complete profile |
| **[4] Add new student** | Guided wizard to create a new student record |
| **[5] Update student info** | Edit name, phone, and address |
| **[6] Change student status** | Set status: `active` / `inactive` / `graduated` / `suspended` |
| **[7] View top performers** | List top N students ranked by GPA |
| **[8] Student statistics** | Counts, average GPA, highest/lowest GPA |

### Adding a Student — Step by Step

1. Select **[4] Add new student**
2. Departments table is shown for reference
3. Enter: First Name, Last Name, Date of Birth (YYYY-MM-DD), Gender, Email
4. Optionally enter Phone and Address
5. Optionally enter a Department ID from the table shown
6. Confirm with **y** — the system auto-generates a Student Code (e.g., `STU20260001`)

> **Note:** The student code is generated automatically by the database using the format `STU{YEAR}{SEQNO}`. You cannot set it manually.

---

## 5. Course Management

Access via **Main Menu → [2]**

| Option | Description |
|---|---|
| **[1] List all courses** | Show active courses with optional semester filter |
| **[2] Search courses** | Search by code or name keyword |
| **[3] View course details** | Full info for a single course |
| **[4] View enrolled students** | See all students enrolled in a course (with marks/grades) |
| **[5] Course enrollment summary** | Table of all courses with seat usage and grade stats |
| **[6] Add new course** | Create a new course |
| **[7] Update course** | Edit name, description, max students |
| **[8] Deactivate course** | Soft-disable a course (it stays in the DB) |

### Understanding the Enrollment Summary

The summary table includes:
- **Enrolled** — current enrollment count
- **Max** — seat capacity
- **Available** — free seats (Enrolled subtracted from Max)
- **Avg Marks** — average total marks across all completed enrollments
- **Pass / Fail** — count of pass and fail results

---

## 6. Enrollment & Marks

Access via **Main Menu → [3]**

| Option | Description |
|---|---|
| **[1] Enroll student in course** | Link a student to a course for a given year/semester |
| **[2] View student enrollments** | All courses for a student, with marks and grades |
| **[3] View course enrollments** | All students in a course |
| **[4] Update marks (single)** | Enter Internal (0–40) and External (0–60) for one enrollment |
| **[5] Bulk marks entry** | Efficient entry for all students in a course/semester |
| **[6] Drop enrollment** | Mark an enrollment as dropped |
| **[7] View grade distribution** | Bar chart and table of grade breakdown for a course |
| **[8] View student transcript** | Full academic record: all courses, marks, CGPA |

### Grade Table

| Marks (out of 100) | Grade | Grade Points |
|---|---|---|
| 90–100 | O (Outstanding) | 10.0 |
| 80–89 | A+ | 9.0 |
| 70–79 | A | 8.0 |
| 60–69 | B+ | 7.0 |
| 50–59 | B | 6.0 |
| 40–49 | C | 5.0 |
| < 40 | F (Fail) | 0.0 |

> Grades are **computed automatically by the database trigger** when marks are saved. You do not need to enter grades manually.

### Bulk Marks Entry

1. Select **[5] Bulk marks entry**
2. Enter the Course ID, academic year, and semester
3. Students for that course/semester are listed one by one
4. For each student, enter Internal marks and External marks
5. Press **Enter** to skip a student (their marks are not changed)
6. Confirm with **y** to save all entered marks at once

---

## 7. Attendance Management

Access via **Main Menu → [4]**

| Option | Description |
|---|---|
| **[1] Mark attendance (single)** | Mark one student for one date |
| **[2] Bulk mark attendance (class)** | Mark entire class in one session |
| **[3] View attendance by date** | See the attendance register for a course on a specific date |
| **[4] View student attendance** | Full attendance history for a student |
| **[5] Attendance summary (course)** | Summary table for all students in a course |
| **[6] Attendance summary (student)** | Per-course attendance breakdown for a student |
| **[7] View defaulters** | Students below a given attendance threshold (default 75%) |
| **[8] List class dates** | All dates attendance was recorded for a course |

### Bulk Attendance Entry (Fast Mode)

When marking attendance for an entire class, the system uses single-letter shortcuts:

| Key | Status |
|---|---|
| `P` | Present |
| `A` | Absent |
| `L` | Late |
| `O` | On Duty (OD) |
| *(Enter)* | Absent (default) |

Example:
```
  STU20240001  Aditya Sharma        : P
  STU20240002  Priyanka Gupta       : L
  STU20240003  Rohan Mehta          : 
```

> **Upsert behaviour:** Re-marking attendance on the same date **overwrites** the previous entry. There is no double-booking.

### Attendance Eligibility

Students require **≥ 75% attendance** to be eligible to sit for exams. The system flags ineligible students with `NO ⚠` in summary tables, and the **View defaulters** option helps identify them quickly.

---

## 8. Reports & Analytics

Access via **Main Menu → [5]**

| Option | Description |
|---|---|
| **[1] System summary dashboard** | Overall student counts, active/graduated breakdown, avg GPA + department table |
| **[2] Department statistics** | Per-department headcount, active students, avg GPA, course count |
| **[3] Top performers (by GPA)** | Ranked list of highest-GPA students |
| **[4] Student transcript (console)** | Full academic record printed to the terminal |
| **[5] Student transcript (export CSV)** | Saves a transcript CSV to the `reports/` folder |
| **[6] Grade distribution (course)** | Grade breakdown with ASCII bar chart for a course |
| **[7] Attendance defaulters (course)** | Students below the attendance threshold |

### Exported Files

CSV transcripts are saved to:
```
reports/transcript_{STUDENT_CODE}_{YYYYMMDD_HHMMSS}.csv
```

---

## 9. Tips & Keyboard Shortcuts

| Action | How |
|---|---|
| Cancel current input | Press **Ctrl+C** |
| Go back to previous menu | Enter **0** |
| Skip optional fields | Press **Enter** (accepts the default shown in `[brackets]`) |
| Confirm prompts | Type **y** and press Enter |

---

## 10. Troubleshooting

### "Connecting to database... FAILED"

1. Verify MySQL is running: `services.msc` → MySQL80
2. Check credentials in `.env` or environment variables
3. Run the test: `python -c "from student_management.config.database import test_connection; test_connection()"`

### "Student not found" after adding

The auto-generated code requires the database trigger to fire. Make sure `schema.sql` was loaded with `setup.sql`.

### GPA shows 0.00 for all students

GPA is recalculated by a DB trigger when marks are updated. Students with no completed enrollments will show 0.00.

### C test harness not compiling

Make sure GCC is installed and on your PATH:
```powershell
gcc --version    # should print version info
cd c_modules
make
```
