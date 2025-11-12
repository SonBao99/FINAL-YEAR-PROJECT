"""Quick database verification script"""
import sqlite3

def main():
    conn = sqlite3.connect('attendance.db')
    cursor = conn.cursor()
    
    print("=" * 50)
    print("Database Verification")
    print("=" * 50)
    
    # Check students
    print("\n=== STUDENTS ===")
    cursor.execute('SELECT id, student_id, name, email FROM students')
    students = cursor.fetchall()
    if students:
        for row in students:
            print(f"  ID: {row[0]}, Student ID: {row[1]}, Name: {row[2]}, Email: {row[3]}")
    else:
        print("  No students found")
    
    # Check sessions
    print("\n=== SESSIONS ===")
    cursor.execute('SELECT id, session_name, is_active, course_id FROM sessions')
    sessions = cursor.fetchall()
    if sessions:
        for row in sessions:
            status = "ACTIVE" if row[2] else "INACTIVE"
            print(f"  ID: {row[0]}, Name: {row[1]}, Status: {status}, Course ID: {row[3]}")
    else:
        print("  No sessions found")
    
    # Check attendance records
    print("\n=== ATTENDANCE RECORDS ===")
    cursor.execute('SELECT id, student_id, session_id, check_in_time FROM attendance_records')
    records = cursor.fetchall()
    print(f"  Total records: {len(records)}")
    if records:
        for row in records:
            print(f"  Record {row[0]}: Student {row[1]}, Session {row[2]}, Time: {row[3]}")
    else:
        print("  No attendance records yet")
    
    # Check courses
    print("\n=== COURSES ===")
    cursor.execute('SELECT id, course_code, course_name, lecturer_name FROM courses')
    courses = cursor.fetchall()
    if courses:
        for row in courses:
            print(f"  ID: {row[0]}, Code: {row[1]}, Name: {row[2]}, Lecturer: {row[3]}")
    else:
        print("  No courses found")
    
    conn.close()
    print("\n" + "=" * 50)

if __name__ == "__main__":
    main()


