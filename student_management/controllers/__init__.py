# student_management/controllers/__init__.py
from .student_controller    import StudentController
from .course_controller     import CourseController
from .enrollment_controller import EnrollmentController
from .attendance_controller import AttendanceController

__all__ = ["StudentController", "CourseController",
           "EnrollmentController", "AttendanceController"]
