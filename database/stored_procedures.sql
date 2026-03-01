-- ============================================================
-- Student Record Management System
-- Stored Procedures
-- ============================================================

USE student_management_db;

-- ============================================================
-- PROCEDURE: sp_add_student
-- Adds a new student with auto-generated student_code
-- ============================================================
DELIMITER $$
CREATE PROCEDURE sp_add_student(
    IN  p_first_name      VARCHAR(50),
    IN  p_last_name       VARCHAR(50),
    IN  p_dob             DATE,
    IN  p_gender          ENUM('Male','Female','Other'),
    IN  p_email           VARCHAR(100),
    IN  p_phone           VARCHAR(15),
    IN  p_address         TEXT,
    IN  p_department_id   INT,
    OUT p_student_id      INT,
    OUT p_student_code    VARCHAR(20),
    OUT p_message         VARCHAR(255)
)
BEGIN
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        GET DIAGNOSTICS CONDITION 1 p_message = MESSAGE_TEXT;
        ROLLBACK;
    END;

    START TRANSACTION;

    INSERT INTO students (first_name, last_name, date_of_birth, gender, email,
                          phone, address, department_id)
    VALUES (p_first_name, p_last_name, p_dob, p_gender, p_email,
            p_phone, p_address, p_department_id);

    SET p_student_id   = LAST_INSERT_ID();
    SELECT student_code INTO p_student_code
    FROM students WHERE student_id = p_student_id;

    SET p_message = CONCAT('Student added successfully. Code: ', p_student_code);
    COMMIT;
END$$
DELIMITER ;


-- ============================================================
-- PROCEDURE: sp_update_student
-- Updates student details
-- ============================================================
DELIMITER $$
CREATE PROCEDURE sp_update_student(
    IN  p_student_id      INT,
    IN  p_first_name      VARCHAR(50),
    IN  p_last_name       VARCHAR(50),
    IN  p_phone           VARCHAR(15),
    IN  p_address         TEXT,
    IN  p_status          ENUM('active','inactive','graduated','suspended'),
    OUT p_message         VARCHAR(255)
)
BEGIN
    DECLARE v_count INT;

    SELECT COUNT(*) INTO v_count FROM students WHERE student_id = p_student_id;
    IF v_count = 0 THEN
        SET p_message = CONCAT('ERROR: Student ID ', p_student_id, ' not found.');
    ELSE
        UPDATE students
        SET first_name = COALESCE(p_first_name, first_name),
            last_name  = COALESCE(p_last_name,  last_name),
            phone      = COALESCE(p_phone,      phone),
            address    = COALESCE(p_address,    address),
            status     = COALESCE(p_status,     status)
        WHERE student_id = p_student_id;

        SET p_message = CONCAT('Student ID ', p_student_id, ' updated successfully.');
    END IF;
END$$
DELIMITER ;


-- ============================================================
-- PROCEDURE: sp_delete_student
-- Soft-deletes a student by setting status = 'inactive'
-- ============================================================
DELIMITER $$
CREATE PROCEDURE sp_delete_student(
    IN  p_student_id  INT,
    OUT p_message     VARCHAR(255)
)
BEGIN
    DECLARE v_count INT;

    SELECT COUNT(*) INTO v_count FROM students WHERE student_id = p_student_id;
    IF v_count = 0 THEN
        SET p_message = CONCAT('ERROR: Student ID ', p_student_id, ' not found.');
    ELSE
        UPDATE students SET status = 'inactive' WHERE student_id = p_student_id;
        SET p_message = CONCAT('Student ID ', p_student_id, ' deactivated.');
    END IF;
END$$
DELIMITER ;


-- ============================================================
-- PROCEDURE: sp_enroll_student
-- Enrolls a student in a course for a given semester/year
-- ============================================================
DELIMITER $$
CREATE PROCEDURE sp_enroll_student(
    IN  p_student_id    INT,
    IN  p_course_id     INT,
    IN  p_faculty_id    INT,
    IN  p_acad_year     YEAR,
    IN  p_semester      ENUM('1','2','3','4','5','6','7','8'),
    OUT p_message       VARCHAR(255)
)
BEGIN
    DECLARE v_enrolled  INT;
    DECLARE v_max       INT;
    DECLARE v_stu_ok    INT;
    DECLARE v_crs_ok    INT;

    -- Validate student
    SELECT COUNT(*) INTO v_stu_ok FROM students
    WHERE student_id = p_student_id AND status = 'active';

    -- Validate course & seat availability
    SELECT COUNT(e.enrollment_id), c.max_students
    INTO v_enrolled, v_max
    FROM courses c
    LEFT JOIN enrollments e ON c.course_id = e.course_id
        AND e.academic_year = p_acad_year AND e.semester = p_semester
    WHERE c.course_id = p_course_id AND c.is_active = TRUE
    GROUP BY c.max_students;

    IF v_stu_ok = 0 THEN
        SET p_message = 'ERROR: Active student not found.';
    ELSEIF v_max IS NULL THEN
        SET p_message = 'ERROR: Course not found or inactive.';
    ELSEIF v_enrolled >= v_max THEN
        SET p_message = 'ERROR: Course is full.';
    ELSE
        INSERT INTO enrollments (student_id, course_id, faculty_id, academic_year, semester)
        VALUES (p_student_id, p_course_id, p_faculty_id, p_acad_year, p_semester);
        SET p_message = 'Student enrolled successfully.';
    END IF;
END$$
DELIMITER ;


-- ============================================================
-- PROCEDURE: sp_update_marks
-- Updates internal + external marks and triggers grade assignment
-- ============================================================
DELIMITER $$
CREATE PROCEDURE sp_update_marks(
    IN  p_enrollment_id   INT,
    IN  p_internal_marks  DECIMAL(5,2),
    IN  p_external_marks  DECIMAL(5,2),
    OUT p_message         VARCHAR(255)
)
BEGIN
    DECLARE v_count INT;

    SELECT COUNT(*) INTO v_count FROM enrollments WHERE enrollment_id = p_enrollment_id;
    IF v_count = 0 THEN
        SET p_message = 'ERROR: Enrollment not found.';
    ELSE
        UPDATE enrollments
        SET internal_marks = p_internal_marks,
            external_marks = p_external_marks,
            status         = 'completed'
        WHERE enrollment_id = p_enrollment_id;

        SET p_message = 'Marks updated and grade assigned.';
    END IF;
END$$
DELIMITER ;


-- ============================================================
-- PROCEDURE: sp_mark_attendance
-- Marks attendance for a student in a course on a given date
-- Supports INSERT or UPDATE (upsert)
-- ============================================================
DELIMITER $$
CREATE PROCEDURE sp_mark_attendance(
    IN  p_student_id  INT,
    IN  p_course_id   INT,
    IN  p_date        DATE,
    IN  p_status      ENUM('Present','Absent','Late','OD'),
    IN  p_marked_by   INT,
    OUT p_message     VARCHAR(255)
)
BEGIN
    INSERT INTO attendance (student_id, course_id, attend_date, status, marked_by)
    VALUES (p_student_id, p_course_id, p_date, p_status, p_marked_by)
    ON DUPLICATE KEY UPDATE
        status     = p_status,
        marked_by  = p_marked_by;

    SET p_message = 'Attendance recorded.';
END$$
DELIMITER ;


-- ============================================================
-- PROCEDURE: sp_get_student_report
-- Returns student details + enrollment + attendance summary
-- ============================================================
DELIMITER $$
CREATE PROCEDURE sp_get_student_report(
    IN p_student_id INT
)
BEGIN
    -- Basic info
    SELECT * FROM vw_student_full_info WHERE student_id = p_student_id;

    -- Enrollment & grades
    SELECT
        c.course_code,
        c.course_name,
        e.academic_year,
        e.semester,
        e.internal_marks,
        e.external_marks,
        e.total_marks,
        e.grade,
        e.grade_points,
        e.result
    FROM enrollments e
    JOIN courses c ON e.course_id = c.course_id
    WHERE e.student_id = p_student_id
    ORDER BY e.academic_year, e.semester;

    -- Attendance summary
    SELECT
        course_code,
        course_name,
        total_classes,
        present_count,
        absent_count,
        attendance_pct
    FROM vw_attendance_summary
    WHERE student_id = p_student_id;
END$$
DELIMITER ;


-- ============================================================
-- PROCEDURE: sp_search_students
-- Flexible search: by name, email, dept, status
-- ============================================================
DELIMITER $$
CREATE PROCEDURE sp_search_students(
    IN p_keyword     VARCHAR(100),
    IN p_dept_id     INT,
    IN p_status      VARCHAR(20)
)
BEGIN
    SELECT
        s.student_id,
        s.student_code,
        CONCAT(s.first_name,' ',s.last_name) AS full_name,
        s.email,
        s.phone,
        d.dept_name,
        s.status,
        s.gpa
    FROM students s
    LEFT JOIN departments d ON s.department_id = d.department_id
    WHERE
        (p_keyword IS NULL OR
            CONCAT(s.first_name,' ',s.last_name) LIKE CONCAT('%',p_keyword,'%') OR
            s.email          LIKE CONCAT('%',p_keyword,'%') OR
            s.student_code   LIKE CONCAT('%',p_keyword,'%'))
    AND (p_dept_id IS NULL OR s.department_id = p_dept_id)
    AND (p_status  IS NULL OR s.status        = p_status)
    ORDER BY s.last_name, s.first_name;
END$$
DELIMITER ;


-- ============================================================
-- PROCEDURE: sp_department_stats
-- Returns headcount, avg GPA, pass rate per department
-- ============================================================
DELIMITER $$
CREATE PROCEDURE sp_department_stats()
BEGIN
    SELECT
        d.dept_code,
        d.dept_name,
        COUNT(DISTINCT s.student_id)                        AS total_students,
        COUNT(DISTINCT CASE WHEN s.status='active' THEN s.student_id END) AS active_students,
        ROUND(AVG(s.gpa), 2)                                AS avg_gpa,
        COUNT(DISTINCT c.course_id)                         AS total_courses,
        ROUND(
            SUM(CASE WHEN e.result='Pass' THEN 1 ELSE 0 END) * 100.0
            / NULLIF(COUNT(e.enrollment_id),0)
        ,2)                                                 AS pass_rate_pct
    FROM departments d
    LEFT JOIN students s    ON d.department_id = s.department_id
    LEFT JOIN courses  c    ON d.department_id = c.department_id
    LEFT JOIN enrollments e ON s.student_id    = e.student_id
    GROUP BY d.dept_code, d.dept_name
    ORDER BY d.dept_name;
END$$
DELIMITER ;
