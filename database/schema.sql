-- ============================================================
-- Student Record Management System
-- Database Schema
-- ============================================================

CREATE DATABASE IF NOT EXISTS student_management_db
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE student_management_db;

-- ============================================================
-- TABLE: departments
-- ============================================================
CREATE TABLE IF NOT EXISTS departments (
    department_id   INT             AUTO_INCREMENT PRIMARY KEY,
    dept_code       VARCHAR(10)     NOT NULL UNIQUE,
    dept_name       VARCHAR(100)    NOT NULL,
    head_of_dept    VARCHAR(100),
    created_at      TIMESTAMP       DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP       DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- ============================================================
-- TABLE: students
-- ============================================================
CREATE TABLE IF NOT EXISTS students (
    student_id      INT             AUTO_INCREMENT PRIMARY KEY,
    student_code    VARCHAR(20)     NOT NULL UNIQUE COMMENT 'e.g. STU2024001',
    first_name      VARCHAR(50)     NOT NULL,
    last_name       VARCHAR(50)     NOT NULL,
    date_of_birth   DATE            NOT NULL,
    gender          ENUM('Male','Female','Other') NOT NULL,
    email           VARCHAR(100)    NOT NULL UNIQUE,
    phone           VARCHAR(15),
    address         TEXT,
    department_id   INT,
    enrollment_date DATE            NOT NULL DEFAULT (CURRENT_DATE),
    status          ENUM('active','inactive','graduated','suspended') 
                                    NOT NULL DEFAULT 'active',
    gpa             DECIMAL(3,2)    DEFAULT 0.00,
    created_at      TIMESTAMP       DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP       DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT fk_student_dept
        FOREIGN KEY (department_id) REFERENCES departments(department_id)
        ON DELETE SET NULL ON UPDATE CASCADE,

    INDEX idx_student_code  (student_code),
    INDEX idx_student_email (email),
    INDEX idx_student_dept  (department_id),
    INDEX idx_student_status(status)
);

-- ============================================================
-- TABLE: courses
-- ============================================================
CREATE TABLE IF NOT EXISTS courses (
    course_id       INT             AUTO_INCREMENT PRIMARY KEY,
    course_code     VARCHAR(15)     NOT NULL UNIQUE COMMENT 'e.g. CS101',
    course_name     VARCHAR(150)    NOT NULL,
    description     TEXT,
    credits         TINYINT         NOT NULL DEFAULT 3,
    department_id   INT,
    semester        ENUM('1','2','3','4','5','6','7','8')  NOT NULL,
    max_students    INT             NOT NULL DEFAULT 60,
    is_active       BOOLEAN         NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMP       DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_course_dept
        FOREIGN KEY (department_id) REFERENCES departments(department_id)
        ON DELETE SET NULL ON UPDATE CASCADE,

    INDEX idx_course_code(course_code),
    INDEX idx_course_dept(department_id)
);

-- ============================================================
-- TABLE: faculty
-- ============================================================
CREATE TABLE IF NOT EXISTS faculty (
    faculty_id      INT             AUTO_INCREMENT PRIMARY KEY,
    faculty_code    VARCHAR(20)     NOT NULL UNIQUE,
    first_name      VARCHAR(50)     NOT NULL,
    last_name       VARCHAR(50)     NOT NULL,
    email           VARCHAR(100)    NOT NULL UNIQUE,
    phone           VARCHAR(15),
    department_id   INT,
    designation     VARCHAR(100),
    is_active       BOOLEAN         NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMP       DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_faculty_dept
        FOREIGN KEY (department_id) REFERENCES departments(department_id)
        ON DELETE SET NULL ON UPDATE CASCADE
);

-- ============================================================
-- TABLE: enrollments
-- ============================================================
CREATE TABLE IF NOT EXISTS enrollments (
    enrollment_id   INT             AUTO_INCREMENT PRIMARY KEY,
    student_id      INT             NOT NULL,
    course_id       INT             NOT NULL,
    faculty_id      INT,
    academic_year   YEAR            NOT NULL,
    semester        ENUM('1','2','3','4','5','6','7','8') NOT NULL,
    internal_marks  DECIMAL(5,2)    DEFAULT NULL COMMENT 'Out of 40',
    external_marks  DECIMAL(5,2)    DEFAULT NULL COMMENT 'Out of 60',
    total_marks     DECIMAL(5,2)    GENERATED ALWAYS AS 
                        (COALESCE(internal_marks,0) + COALESCE(external_marks,0)) STORED,
    grade           CHAR(2)         DEFAULT NULL,
    grade_points    DECIMAL(3,1)    DEFAULT NULL,
    result          ENUM('Pass','Fail','Incomplete','Withheld') DEFAULT NULL,
    enrollment_date DATE            NOT NULL DEFAULT (CURRENT_DATE),
    status          ENUM('enrolled','dropped','completed') NOT NULL DEFAULT 'enrolled',
    created_at      TIMESTAMP       DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP       DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT fk_enroll_student
        FOREIGN KEY (student_id) REFERENCES students(student_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_enroll_course
        FOREIGN KEY (course_id)  REFERENCES courses(course_id)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_enroll_faculty
        FOREIGN KEY (faculty_id) REFERENCES faculty(faculty_id)
        ON DELETE SET NULL ON UPDATE CASCADE,

    UNIQUE KEY uq_student_course_sem (student_id, course_id, academic_year, semester),
    INDEX idx_enroll_student (student_id),
    INDEX idx_enroll_course  (course_id),
    INDEX idx_enroll_year_sem(academic_year, semester)
);

-- ============================================================
-- TABLE: attendance
-- ============================================================
CREATE TABLE IF NOT EXISTS attendance (
    attendance_id   INT             AUTO_INCREMENT PRIMARY KEY,
    student_id      INT             NOT NULL,
    course_id       INT             NOT NULL,
    attend_date     DATE            NOT NULL,
    status          ENUM('Present','Absent','Late','OD') NOT NULL DEFAULT 'Absent',
    remarks         VARCHAR(255),
    marked_by       INT             COMMENT 'faculty_id who marked attendance',
    created_at      TIMESTAMP       DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_attend_student
        FOREIGN KEY (student_id)  REFERENCES students(student_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_attend_course
        FOREIGN KEY (course_id)   REFERENCES courses(course_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_attend_faculty
        FOREIGN KEY (marked_by)   REFERENCES faculty(faculty_id)
        ON DELETE SET NULL ON UPDATE CASCADE,

    UNIQUE KEY uq_student_course_date (student_id, course_id, attend_date),
    INDEX idx_attend_student (student_id),
    INDEX idx_attend_course  (course_id),
    INDEX idx_attend_date    (attend_date)
);

-- ============================================================
-- TABLE: users  (authentication)
-- ============================================================
CREATE TABLE IF NOT EXISTS users (
    user_id         INT             AUTO_INCREMENT PRIMARY KEY,
    username        VARCHAR(50)     NOT NULL UNIQUE,
    password_hash   VARCHAR(255)    NOT NULL,
    role            ENUM('admin','faculty','student') NOT NULL DEFAULT 'student',
    reference_id    INT             COMMENT 'student_id or faculty_id depending on role',
    is_active       BOOLEAN         NOT NULL DEFAULT TRUE,
    last_login      TIMESTAMP       NULL,
    created_at      TIMESTAMP       DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP       DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    INDEX idx_user_role (role),
    INDEX idx_user_ref  (reference_id)
);

-- ============================================================
-- TABLE: audit_log  (tracks all changes)
-- ============================================================
CREATE TABLE IF NOT EXISTS audit_log (
    log_id          BIGINT          AUTO_INCREMENT PRIMARY KEY,
    table_name      VARCHAR(50)     NOT NULL,
    record_id       INT             NOT NULL,
    action          ENUM('INSERT','UPDATE','DELETE') NOT NULL,
    old_values      JSON,
    new_values      JSON,
    changed_by      INT             COMMENT 'user_id',
    changed_at      TIMESTAMP       DEFAULT CURRENT_TIMESTAMP,

    INDEX idx_log_table  (table_name),
    INDEX idx_log_record (record_id),
    INDEX idx_log_time   (changed_at)
);

-- ============================================================
-- TRIGGER: Auto-generate student_code on INSERT
-- ============================================================
DELIMITER $$
CREATE TRIGGER trg_student_code_before_insert
BEFORE INSERT ON students
FOR EACH ROW
BEGIN
    DECLARE next_id INT;
    IF NEW.student_code IS NULL OR NEW.student_code = '' THEN
        SELECT AUTO_INCREMENT INTO next_id
        FROM information_schema.TABLES
        WHERE TABLE_SCHEMA = DATABASE()
          AND TABLE_NAME   = 'students';
        SET NEW.student_code = CONCAT('STU', YEAR(CURRENT_DATE), LPAD(next_id, 4, '0'));
    END IF;
END$$
DELIMITER ;

-- ============================================================
-- TRIGGER: Auto-assign grade after marks update
-- ============================================================
DELIMITER $$
CREATE TRIGGER trg_assign_grade_after_update
BEFORE UPDATE ON enrollments
FOR EACH ROW
BEGIN
    IF NEW.internal_marks IS NOT NULL AND NEW.external_marks IS NOT NULL THEN
        SET NEW.total_marks = NEW.internal_marks + NEW.external_marks;
        CASE
            WHEN NEW.total_marks >= 90 THEN SET NEW.grade = 'O',  NEW.grade_points = 10.0;
            WHEN NEW.total_marks >= 80 THEN SET NEW.grade = 'A+', NEW.grade_points = 9.0;
            WHEN NEW.total_marks >= 70 THEN SET NEW.grade = 'A',  NEW.grade_points = 8.0;
            WHEN NEW.total_marks >= 60 THEN SET NEW.grade = 'B+', NEW.grade_points = 7.0;
            WHEN NEW.total_marks >= 50 THEN SET NEW.grade = 'B',  NEW.grade_points = 6.0;
            WHEN NEW.total_marks >= 40 THEN SET NEW.grade = 'C',  NEW.grade_points = 5.0;
            ELSE                             SET NEW.grade = 'F',  NEW.grade_points = 0.0;
        END CASE;
        SET NEW.result = IF(NEW.total_marks >= 40, 'Pass', 'Fail');
    END IF;
END$$
DELIMITER ;

-- ============================================================
-- TRIGGER: Recalculate student GPA after enrollment update
-- ============================================================
DELIMITER $$
CREATE TRIGGER trg_update_gpa_after_enrollment
AFTER UPDATE ON enrollments
FOR EACH ROW
BEGIN
    DECLARE avg_gp DECIMAL(3,2);
    IF NEW.grade_points IS NOT NULL THEN
        SELECT ROUND(SUM(c.credits * e.grade_points) / SUM(c.credits), 2)
        INTO avg_gp
        FROM enrollments e
        JOIN courses c ON e.course_id = c.course_id
        WHERE e.student_id  = NEW.student_id
          AND e.grade_points IS NOT NULL
          AND e.status = 'completed';

        UPDATE students SET gpa = COALESCE(avg_gp, 0.00)
        WHERE student_id = NEW.student_id;
    END IF;
END$$
DELIMITER ;

-- ============================================================
-- VIEW: student_full_info
-- ============================================================
CREATE OR REPLACE VIEW vw_student_full_info AS
SELECT
    s.student_id,
    s.student_code,
    CONCAT(s.first_name, ' ', s.last_name)  AS full_name,
    s.email,
    s.phone,
    s.date_of_birth,
    s.gender,
    s.status,
    s.gpa,
    d.dept_name                             AS department,
    s.enrollment_date
FROM students s
LEFT JOIN departments d ON s.department_id = d.department_id;

-- ============================================================
-- VIEW: course_enrollment_summary
-- ============================================================
CREATE OR REPLACE VIEW vw_course_enrollment_summary AS
SELECT
    c.course_id,
    c.course_code,
    c.course_name,
    c.credits,
    d.dept_name                             AS department,
    COUNT(e.enrollment_id)                  AS enrolled_count,
    c.max_students,
    ROUND(AVG(e.total_marks), 2)            AS avg_marks,
    SUM(CASE WHEN e.result = 'Pass' THEN 1 ELSE 0 END) AS pass_count,
    SUM(CASE WHEN e.result = 'Fail' THEN 1 ELSE 0 END) AS fail_count
FROM courses c
LEFT JOIN departments d   ON c.department_id = d.department_id
LEFT JOIN enrollments e   ON c.course_id     = e.course_id
GROUP BY c.course_id, c.course_code, c.course_name, c.credits, d.dept_name, c.max_students;

-- ============================================================
-- VIEW: student_attendance_summary
-- ============================================================
CREATE OR REPLACE VIEW vw_attendance_summary AS
SELECT
    a.student_id,
    s.student_code,
    CONCAT(s.first_name,' ',s.last_name)    AS student_name,
    a.course_id,
    c.course_code,
    c.course_name,
    COUNT(*)                                AS total_classes,
    SUM(CASE WHEN a.status = 'Present' THEN 1 ELSE 0 END) AS present_count,
    SUM(CASE WHEN a.status = 'Absent'  THEN 1 ELSE 0 END) AS absent_count,
    SUM(CASE WHEN a.status = 'Late'    THEN 1 ELSE 0 END) AS late_count,
    ROUND(
        SUM(CASE WHEN a.status IN ('Present','Late','OD') THEN 1 ELSE 0 END) * 100.0 / COUNT(*),
    2)                                      AS attendance_pct
FROM attendance a
JOIN students s ON a.student_id = s.student_id
JOIN courses  c ON a.course_id  = c.course_id
GROUP BY a.student_id, s.student_code, student_name, a.course_id, c.course_code, c.course_name;
