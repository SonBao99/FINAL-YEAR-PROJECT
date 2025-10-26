import unittest
# We are importing the class we want to test.
# For this to work, you would have an 'attendance_tracker.py' file
# in the same directory.
from attendance_tracker import AttendanceTracker

class TestAttendanceTracker(unittest.TestCase):
    """
    Test suite for the AttendanceTracker class.
    Each method in this class that starts with 'test_' is a separate test.
    """

    def setUp(self):
        """
        This method is called before each test function is executed.
        It's used to set up a clean state for every test.
        """
        self.class_roster = ["student_01", "student_02", "student_03", "student_04"]
        self.tracker = AttendanceTracker(self.class_roster)
        print("\nSetting up for a new test...")

    def test_initialization(self):
        """
        Tests if the tracker initializes correctly with an empty attendance list
        and the correct list of absent students.
        """
        print("Testing initial state...")
        # Assert that the list of present students is initially empty
        self.assertEqual(len(self.tracker.get_attendance_list()), 0)
        # Assert that the list of absent students matches the full roster initially
        self.assertCountEqual(self.tracker.get_absent_students(), self.class_roster)

    def test_mark_present(self):
        """
        Tests if a student can be successfully marked as present.
        """
        print("Testing marking a student present...")
        student_to_mark = "student_02"
        self.tracker.mark_present(student_to_mark)
        # Assert that the student now appears in the present list
        self.assertIn(student_to_mark, self.tracker.get_attendance_list())
        # Assert that the student is no longer in the absent list
        self.assertNotIn(student_to_mark, self.tracker.get_absent_students())

    def test_mark_multiple_students_present(self):
        """
        Tests marking several students and verifying the final state.
        """
        print("Testing marking multiple students...")
        students_to_mark = ["student_01", "student_03"]
        self.tracker.mark_present(students_to_mark[0])
        self.tracker.mark_present(students_to_mark[1])
        # Assert that the present list contains exactly the marked students
        self.assertCountEqual(self.tracker.get_attendance_list(), students_to_mark)
        # Assert that the absent list contains the remaining students
        absent_students = ["student_02", "student_04"]
        self.assertCountEqual(self.tracker.get_absent_students(), absent_students)

    def test_mark_non_roster_student(self):
        """
        Tests that the system raises an error when trying to mark a student
        who is not on the class roster.
        """
        print("Testing marking a non-roster student...")
        non_roster_student = "student_99"
        # 'assertRaises' is a context manager that checks if a specific exception is raised.
        # The test passes if a ValueError occurs, and fails otherwise.
        with self.assertRaises(ValueError):
            self.tracker.mark_present(non_roster_student)

    def test_idempotency_of_marking_present(self):
        """
        Tests that marking the same student present multiple times does not change the outcome.
        The attendance list should not contain duplicates.
        """
        print("Testing idempotency of marking present...")
        student_to_mark = "student_04"
        self.tracker.mark_present(student_to_mark)
        initial_list = self.tracker.get_attendance_list()
        
        # Mark the same student again
        self.tracker.mark_present(student_to_mark)
        second_list = self.tracker.get_attendance_list()

        # The list of present students should not have changed in size or content
        self.assertEqual(len(initial_list), 1)
        self.assertEqual(len(second_list), 1)
        self.assertEqual(initial_list, second_list)

# This allows the test to be run from the command line
if __name__ == '__main__':
    unittest.main()

