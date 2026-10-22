import mysql.connector
from mysql.connector import Error

class StudentManagementSystem:
    def __init__(self):
        try:
            self.connection = mysql.connector.connect(
                host='localhost',
                database='student_management',
                user='root',
                password=''  # Default XAMPP password is empty
            )
            if self.connection.is_connected():
                print("Connected to MySQL database")
        except Error as e:
            print(f"Error while connecting to MySQL: {e}")

    def __del__(self):
        if hasattr(self, 'connection') and self.connection.is_connected():
            self.connection.close()
            print("MySQL connection is closed")

    def add_student(self, name, email, phone, course):
        try:
            cursor = self.connection.cursor()
            query = "INSERT INTO students (name, email, phone, course) VALUES (%s, %s, %s, %s)"
            cursor.execute(query, (name, email, phone, course))
            self.connection.commit()
            print("Student added successfully")
        except Error as e:
            print(f"Error adding student: {e}")

    def view_students(self):
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM students")
            students = cursor.fetchall()
            
            if not students:
                print("No students found")
                return
            
            print("\nStudent Records:")
            print("-" * 70)
            print(f"{'ID':<5}{'Name':<20}{'Email':<25}{'Phone':<15}{'Course':<15}")
            print("-" * 70)
            
            for student in students:
                print(f"{student[0]:<5}{student[1]:<20}{student[2]:<25}{student[3]:<15}{student[4]:<15}")
            
            print("-" * 70)
        except Error as e:
            print(f"Error viewing students: {e}")

    def update_student(self, student_id, name=None, email=None, phone=None, course=None):
        try:
            cursor = self.connection.cursor()
            
            # Build the update query based on provided fields
            updates = []
            params = []
            
            if name:
                updates.append("name = %s")
                params.append(name)
            if email:
                updates.append("email = %s")
                params.append(email)
            if phone:
                updates.append("phone = %s")
                params.append(phone)
            if course:
                updates.append("course = %s")
                params.append(course)
                
            if not updates:
                print("No fields to update")
                return
                
            query = f"UPDATE students SET {', '.join(updates)} WHERE id = %s"
            params.append(student_id)
            
            cursor.execute(query, tuple(params))
            self.connection.commit()
            
            if cursor.rowcount > 0:
                print("Student updated successfully")
            else:
                print("No student found with the given ID")
        except Error as e:
            print(f"Error updating student: {e}")

    def delete_student(self, student_id):
        try:
            cursor = self.connection.cursor()
            cursor.execute("DELETE FROM students WHERE id = %s", (student_id,))
            self.connection.commit()
            
            if cursor.rowcount > 0:
                print("Student deleted successfully")
            else:
                print("No student found with the given ID")
        except Error as e:
            print(f"Error deleting student: {e}")

def main():
    sms = StudentManagementSystem()
    
    while True:
        print("\nStudent Management System")
        print("1. Add Student")
        print("2. View Students")
        print("3. Update Student")
        print("4. Delete Student")
        print("5. Exit")
        
        choice = input("Enter your choice (1-5): ")
        
        if choice == '1':
            print("\nAdd New Student")
            name = input("Name: ")
            email = input("Email: ")
            phone = input("Phone: ")
            course = input("Course: ")
            sms.add_student(name, email, phone, course)
            
        elif choice == '2':
            sms.view_students()
            
        elif choice == '3':
            student_id = int(input("Enter student ID to update: "))
            print("Leave field blank to keep current value")
            name = input("Name: ")
            email = input("Email: ")
            phone = input("Phone: ")
            course = input("Course: ")
            
            # Only pass fields that have values
            update_data = {}
            if name: update_data['name'] = name
            if email: update_data['email'] = email
            if phone: update_data['phone'] = phone
            if course: update_data['course'] = course
            
            sms.update_student(student_id, **update_data)
            
        elif choice == '4':
            student_id = int(input("Enter student ID to delete: "))
            sms.delete_student(student_id)
            
        elif choice == '5':
            print("Exiting program...")
            break
            
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()