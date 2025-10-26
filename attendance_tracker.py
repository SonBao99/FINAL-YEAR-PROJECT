class AttendanceTracker:
    """
    Manages attendance for a single class session.
    It tracks which students from a roster are present or absent.
    """
    def __init__(self, class_roster):
        """
        Initializes the tracker with a set of student IDs.

        Args:
            class_roster (list or set): A collection of unique student IDs.
        """
        self.roster = set(class_roster)
        self.present_students = set()

    def mark_present(self, student_id):
        """
        Marks a single student as present.

        Args:
            student_id (str): The ID of the student to mark as present.

        Raises:
            ValueError: If the student_id is not found in the class roster.
        """
        if student_id not in self.roster:
            raise ValueError(f"Student '{student_id}' is not in the class roster.")
        self.present_students.add(student_id)

    def get_absent_students(self):
        """
        Returns a set of students who are on the roster but not marked present.

        Returns:
            set: A set of student IDs for absent students.
        """
        return self.roster - self.present_students

    def get_attendance_list(self):
        """
        Returns a sorted list of students who are marked present.

        Returns:
            list: A sorted list of student IDs.
        """
        return sorted(list(self.present_students))
