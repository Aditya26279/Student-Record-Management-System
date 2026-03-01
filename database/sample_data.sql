-- ============================================================
-- Student Record Management System
-- Sample / Seed Data
-- ============================================================

USE student_management_db;

-- ============================================================
-- Departments
-- ============================================================
INSERT INTO departments (dept_code, dept_name, head_of_dept) VALUES
('CS',   'Computer Science & Engineering',       'Dr. Rajesh Kumar'),
('IT',   'Information Technology',               'Dr. Priya Sharma'),
('EC',   'Electronics & Communication Engg.',    'Dr. Anil Verma'),
('ME',   'Mechanical Engineering',               'Dr. Suresh Nair'),
('CE',   'Civil Engineering',                    'Dr. Meena Iyer'),
('EE',   'Electrical Engineering',               'Dr. Vikram Singh'),
('MBA',  'Master of Business Administration',    'Dr. Anita Desai');

-- ============================================================
-- Faculty
-- ============================================================
INSERT INTO faculty (faculty_code, first_name, last_name, email, phone, department_id, designation) VALUES
('FAC001', 'Rajesh',  'Kumar',  'rajesh.kumar@university.edu',  '9876543210', 1, 'Professor & HOD'),
('FAC002', 'Priya',   'Sharma', 'priya.sharma@university.edu',  '9876543211', 2, 'Professor & HOD'),
('FAC003', 'Anil',    'Verma',  'anil.verma@university.edu',    '9876543212', 3, 'Professor & HOD'),
('FAC004', 'Kavitha', 'Rao',    'kavitha.rao@university.edu',   '9876543213', 1, 'Associate Professor'),
('FAC005', 'Mahesh',  'Patel',  'mahesh.patel@university.edu',  '9876543214', 1, 'Assistant Professor'),
('FAC006', 'Sunitha', 'Nair',   'sunitha.nair@university.edu',  '9876543215', 2, 'Associate Professor'),
('FAC007', 'Vinod',   'Mishra', 'vinod.mishra@university.edu',  '9876543216', 3, 'Assistant Professor');

-- ============================================================
-- Courses
-- ============================================================
INSERT INTO courses (course_code, course_name, description, credits, department_id, semester, max_students) VALUES
-- CS Department
('CS101', 'Introduction to Programming',        'Basics of programming using C',                     4, 1, '1', 60),
('CS102', 'Digital Logic Design',               'Boolean algebra and logic gates',                   3, 1, '1', 60),
('CS201', 'Data Structures & Algorithms',       'Arrays, linked lists, trees, graphs',               4, 1, '2', 60),
('CS202', 'Object-Oriented Programming',         'OOP concepts using Java',                           4, 1, '2', 60),
('CS301', 'Database Management Systems',         'RDBMS concepts, SQL, normalization',                4, 1, '3', 60),
('CS302', 'Operating Systems',                   'Process management, memory, file systems',          4, 1, '3', 60),
('CS401', 'Computer Networks',                   'OSI model, TCP/IP, protocols',                      4, 1, '4', 60),
('CS402', 'Software Engineering',                'SDLC, design patterns, testing',                    3, 1, '4', 60),
('CS501', 'Machine Learning',                    'Supervised and unsupervised learning',              4, 1, '5', 40),
('CS502', 'Web Technologies',                    'HTML, CSS, JS, PHP, frameworks',                    3, 1, '5', 60),
-- IT Department
('IT101', 'Fundamentals of IT',                  'Overview of IT systems',                            3, 2, '1', 60),
('IT201', 'Network Security',                    'Cryptography and security protocols',               4, 2, '3', 50),
-- EC Department
('EC101', 'Electronic Devices & Circuits',       'Semiconductor devices, amplifiers',                 4, 3, '1', 60),
('EC201', 'Signals & Systems',                   'Signal processing fundamentals',                    4, 3, '2', 60);

-- ============================================================
-- Students
-- ============================================================
INSERT INTO students (student_code, first_name, last_name, date_of_birth, gender, email, phone, address, department_id, enrollment_date, status) VALUES
('STU20240001','Aditya',   'Sharma',   '2005-03-15','Male',  'aditya.sharma@student.edu',   '9100000001','101 MG Road, Bangalore',    1,'2024-06-01','active'),
('STU20240002','Priyanka', 'Gupta',    '2005-07-22','Female','priyanka.gupta@student.edu',  '9100000002','22 Park Street, Delhi',      1,'2024-06-01','active'),
('STU20240003','Rohan',    'Mehta',    '2005-01-10','Male',  'rohan.mehta@student.edu',     '9100000003','5 Lake View, Pune',          1,'2024-06-01','active'),
('STU20240004','Sneha',    'Patil',    '2005-05-30','Female','sneha.patil@student.edu',     '9100000004','88 Anna Salai, Chennai',     2,'2024-06-01','active'),
('STU20240005','Karan',    'Singh',    '2004-11-18','Male',  'karan.singh@student.edu',     '9100000005','15 Civil Lines, Jaipur',     2,'2024-06-01','active'),
('STU20240006','Ananya',   'Iyer',     '2005-09-05','Female','ananya.iyer@student.edu',     '9100000006','3 Nungambakkam, Chennai',    3,'2024-06-01','active'),
('STU20240007','Vikram',   'Reddy',    '2005-02-28','Male',  'vikram.reddy@student.edu',    '9100000007','7 Hitech City, Hyderabad',   3,'2024-06-01','active'),
('STU20240008','Meera',    'Nair',     '2005-06-14','Female','meera.nair@student.edu',      '9100000008','9 Koramangala, Bangalore',   1,'2024-06-01','active'),
('STU20240009','Arjun',    'Patel',    '2005-04-03','Male',  'arjun.patel@student.edu',     '9100000009','44 Ellis Bridge, Ahmedabad', 1,'2024-06-01','active'),
('STU20240010','Divya',    'Kumar',    '2005-08-19','Female','divya.kumar@student.edu',     '9100000010','12 Shanti Nagar, Bhopal',    2,'2024-06-01','active'),
('STU20230001','Rahul',    'Joshi',    '2004-12-07','Male',  'rahul.joshi@student.edu',     '9100000011','67 Deccan Gymkhana, Pune',   1,'2023-06-01','active'),
('STU20230002','Kavya',    'Menon',    '2004-03-25','Female','kavya.menon@student.edu',     '9100000012','2 Marine Drive, Mumbai',     1,'2023-06-01','active'),
('STU20230003','Siddharth','Chauhan', '2003-08-11','Male',  'siddharth.c@student.edu',     '9100000013','30 Rajouri Garden, Delhi',   1,'2022-06-01','graduated'),
('STU20230004','Pooja',    'Verma',    '2004-01-29','Female','pooja.verma@student.edu',     '9100000014','56 Salt Lake City, Kolkata', 2,'2023-06-01','active'),
('STU20230005','Nikhil',   'Bose',     '2004-06-17','Male',  'nikhil.bose@student.edu',     '9100000015','71 Camac Street, Kolkata',   3,'2023-06-01','active');

-- ============================================================
-- Enrollments (2024 batch — Semester 1)
-- ============================================================
INSERT INTO enrollments (student_id, course_id, faculty_id, academic_year, semester, internal_marks, external_marks, status) VALUES
-- Aditya Sharma → CS101, CS102
(1, 1, 5, 2024, '1', 35, 55, 'completed'),
(1, 2, 4, 2024, '1', 30, 48, 'completed'),
-- Priyanka Gupta → CS101, CS102
(2, 1, 5, 2024, '1', 38, 58, 'completed'),
(2, 2, 4, 2024, '1', 33, 52, 'completed'),
-- Rohan Mehta → CS101, CS102
(3, 1, 5, 2024, '1', 28, 42, 'completed'),
(3, 2, 4, 2024, '1', 25, 35, 'completed'),
-- Sneha Patil → IT101
(4, 11, 6, 2024, '1', 36, 56, 'completed'),
-- Karan Singh → IT101
(5, 11, 6, 2024, '1', 32, 50, 'completed'),
-- Ananya Iyer → EC101
(6, 13, 7, 2024, '1', 37, 57, 'completed'),
-- Vikram Reddy → EC101
(7, 13, 7, 2024, '1', 29, 44, 'completed'),
-- Meera Nair → CS101, CS102
(8, 1, 5, 2024, '1', 39, 59, 'completed'),
(8, 2, 4, 2024, '1', 36, 55, 'completed'),
-- Arjun Patel → CS101
(9, 1, 5, 2024, '1', 31, 49, 'completed'),
-- Divya Kumar → IT101
(10, 11, 6, 2024, '1', 34, 54, 'completed');

-- 2023 batch → Semester 3 (older students taking advanced courses)
INSERT INTO enrollments (student_id, course_id, faculty_id, academic_year, semester, internal_marks, external_marks, status) VALUES
(11, 3, 4, 2024, '3', 33, 55, 'completed'),   -- Rahul → CS201
(11, 5, 1, 2024, '3', 37, 58, 'completed'),   -- Rahul → CS301
(12, 3, 4, 2024, '3', 35, 56, 'completed'),   -- Kavya → CS201
(12, 5, 1, 2024, '3', 38, 60, 'completed'),   -- Kavya → CS301
(14, 11,6, 2024, '3', 30, 47, 'completed'),   -- Pooja → IT101 (retake)
(15, 13, 7, 2024, '3', 34, 52, 'completed');  -- Nikhil → EC201

-- ============================================================
-- Attendance (sample for CS101 — first 5 days)
-- ============================================================
INSERT INTO attendance (student_id, course_id, attend_date, status, marked_by) VALUES
-- Day 1: 2024-08-01
(1,1,'2024-08-01','Present',5), (2,1,'2024-08-01','Present',5), (3,1,'2024-08-01','Absent',5),
(8,1,'2024-08-01','Present',5), (9,1,'2024-08-01','Late',   5),
-- Day 2: 2024-08-05
(1,1,'2024-08-05','Present',5), (2,1,'2024-08-05','Present',5), (3,1,'2024-08-05','Present',5),
(8,1,'2024-08-05','Present',5), (9,1,'2024-08-05','Present',5),
-- Day 3: 2024-08-08
(1,1,'2024-08-08','Late',   5), (2,1,'2024-08-08','Present',5), (3,1,'2024-08-08','Absent',5),
(8,1,'2024-08-08','Present',5), (9,1,'2024-08-08','Absent', 5),
-- Day 4: 2024-08-12
(1,1,'2024-08-12','Present',5), (2,1,'2024-08-12','Present',5), (3,1,'2024-08-12','Present',5),
(8,1,'2024-08-12','Present',5), (9,1,'2024-08-12','Present',5),
-- Day 5: 2024-08-15
(1,1,'2024-08-15','OD',     5), (2,1,'2024-08-15','Present',5), (3,1,'2024-08-15','Absent',5),
(8,1,'2024-08-15','Present',5), (9,1,'2024-08-15','Present',5);

-- ============================================================
-- Users (admin + faculty + student login accounts)
-- Passwords are SHA2-256 hashed: default = 'Password@123'
-- SHA2('Password@123', 256)
-- ============================================================
INSERT INTO users (username, password_hash, role, reference_id) VALUES
('admin',           SHA2('Admin@123',    256), 'admin',   NULL),
('rajesh.kumar',    SHA2('Password@123', 256), 'faculty', 1),
('priya.sharma',    SHA2('Password@123', 256), 'faculty', 2),
('aditya.sharma',   SHA2('Password@123', 256), 'student', 1),
('priyanka.gupta',  SHA2('Password@123', 256), 'student', 2),
('rohan.mehta',     SHA2('Password@123', 256), 'student', 3),
('meera.nair',      SHA2('Password@123', 256), 'student', 8);
