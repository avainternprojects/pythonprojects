import mysql.connector
from mysql.connector import Error
import tkinter as tk
from tkinter import ttk, messagebox

class StudentManagementApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Student Management System")
        self.root.geometry("900x600")
        
        # Database connection
        self.db_connection = None
        self.connect_to_db()
        
        # GUI Components
        self.create_widgets()
        self.load_students()

    def connect_to_db(self):
        try:
            self.db_connection = mysql.connector.connect(
                host='localhost',
                database='college_management',
                user='root',
                password=''
            )
        except Error as e:
            messagebox.showerror("Database Error", f"Failed to connect to database: {e}")
            self.root.destroy()

    def create_widgets(self):
        # Frame for form
        form_frame = ttk.LabelFrame(self.root, text="Student Form", padding=(10, 5))
        form_frame.pack(fill=tk.X, padx=10, pady=5)

        # Form fields
        ttk.Label(form_frame, text="Name:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.name_entry = ttk.Entry(form_frame, width=30)
        self.name_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(form_frame, text="Email:").grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        self.email_entry = ttk.Entry(form_frame, width=30)
        self.email_entry.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(form_frame, text="Phone:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.phone_entry = ttk.Entry(form_frame, width=30)
        self.phone_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(form_frame, text="Course:").grid(row=1, column=2, padx=5, pady=5, sticky=tk.W)
        self.course_entry = ttk.Entry(form_frame, width=30)
        self.course_entry.grid(row=1, column=3, padx=5, pady=5)

        # Buttons
        button_frame = ttk.Frame(self.root)
        button_frame.pack(fill=tk.X, padx=10, pady=5)

        self.add_button = ttk.Button(button_frame, text="Add", command=self.add_student)
        self.add_button.pack(side=tk.LEFT, padx=5)

        self.update_button = ttk.Button(button_frame, text="Update", command=self.update_student, state=tk.DISABLED)
        self.update_button.pack(side=tk.LEFT, padx=5)

        self.delete_button = ttk.Button(button_frame, text="Delete", command=self.delete_student, state=tk.DISABLED)
        self.delete_button.pack(side=tk.LEFT, padx=5)

        self.clear_button = ttk.Button(button_frame, text="Clear", command=self.clear_form)
        self.clear_button.pack(side=tk.LEFT, padx=5)

        # Treeview for student list
        tree_frame = ttk.LabelFrame(self.root, text="Student Records", padding=(10, 5))
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.tree = ttk.Treeview(tree_frame, columns=('ID', 'Name', 'Email', 'Phone', 'Course'), show='headings')
        
        # Configure columns
        self.tree.heading('ID', text='ID', anchor=tk.W)
        self.tree.heading('Name', text='Name', anchor=tk.W)
        self.tree.heading('Email', text='Email', anchor=tk.W)
        self.tree.heading('Phone', text='Phone', anchor=tk.W)
        self.tree.heading('Course', text='Course', anchor=tk.W)

        self.tree.column('ID', width=50, minwidth=50)
        self.tree.column('Name', width=150, minwidth=150)
        self.tree.column('Email', width=200, minwidth=200)
        self.tree.column('Phone', width=100, minwidth=100)
        self.tree.column('Course', width=150, minwidth=150)

        # Add scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(fill=tk.BOTH, expand=True)

        # Bind treeview selection
        self.tree.bind('<<TreeviewSelect>>', self.on_tree_select)

    def load_students(self):
        # Clear existing data
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        try:
            cursor = self.db_connection.cursor()
            cursor.execute("SELECT * FROM students ORDER BY name")
            students = cursor.fetchall()
            
            for student in students:
                self.tree.insert('', tk.END, values=student)
                
        except Error as e:
            messagebox.showerror("Database Error", f"Failed to load students: {e}")

    def add_student(self):
        name = self.name_entry.get()
        email = self.email_entry.get()
        phone = self.phone_entry.get()
        course = self.course_entry.get()
        
        if not name or not email:
            messagebox.showwarning("Input Error", "Name and Email are required fields")
            return
            
        try:
            cursor = self.db_connection.cursor()
            query = "INSERT INTO students (name, email, phone, course) VALUES (%s, %s, %s, %s)"
            cursor.execute(query, (name, email, phone, course))
            self.db_connection.commit()
            
            messagebox.showinfo("Success", "Student added successfully")
            self.clear_form()
            self.load_students()
            
        except Error as e:
            messagebox.showerror("Database Error", f"Failed to add student: {e}")

    def update_student(self):
        selected_item = self.tree.selection()
        if not selected_item:
            return
            
        student_id = self.tree.item(selected_item)['values'][0]
        name = self.name_entry.get()
        email = self.email_entry.get()
        phone = self.phone_entry.get()
        course = self.course_entry.get()
        
        try:
            cursor = self.db_connection.cursor()
            query = "UPDATE students SET name=%s, email=%s, phone=%s, course=%s WHERE id=%s"
            cursor.execute(query, (name, email, phone, course, student_id))
            self.db_connection.commit()
            
            messagebox.showinfo("Success", "Student updated successfully")
            self.clear_form()
            self.load_students()
            
        except Error as e:
            messagebox.showerror("Database Error", f"Failed to update student: {e}")

    def delete_student(self):
        selected_item = self.tree.selection()
        if not selected_item:
            return
            
        student_id = self.tree.item(selected_item)['values'][0]
        
        if not messagebox.askyesno("Confirm", "Are you sure you want to delete this student?"):
            return
            
        try:
            cursor = self.db_connection.cursor()
            cursor.execute("DELETE FROM students WHERE id=%s", (student_id,))
            self.db_connection.commit()
            
            messagebox.showinfo("Success", "Student deleted successfully")
            self.clear_form()
            self.load_students()
            
        except Error as e:
            messagebox.showerror("Database Error", f"Failed to delete student: {e}")

    def clear_form(self):
        self.name_entry.delete(0, tk.END)
        self.email_entry.delete(0, tk.END)
        self.phone_entry.delete(0, tk.END)
        self.course_entry.delete(0, tk.END)
        
        self.update_button.config(state=tk.DISABLED)
        self.delete_button.config(state=tk.DISABLED)
        self.add_button.config(state=tk.NORMAL)

    def on_tree_select(self, event):
        selected_item = self.tree.selection()
        if not selected_item:
            return
            
        student_data = self.tree.item(selected_item)['values']
        
        self.name_entry.delete(0, tk.END)
        self.name_entry.insert(0, student_data[1])
        
        self.email_entry.delete(0, tk.END)
        self.email_entry.insert(0, student_data[2])
        
        self.phone_entry.delete(0, tk.END)
        self.phone_entry.insert(0, student_data[3])
        
        self.course_entry.delete(0, tk.END)
        self.course_entry.insert(0, student_data[4])
        
        self.update_button.config(state=tk.NORMAL)
        self.delete_button.config(state=tk.NORMAL)
        self.add_button.config(state=tk.DISABLED)

    def __del__(self):
        if self.db_connection and self.db_connection.is_connected():
            self.db_connection.close()

if __name__ == "__main__":
    root = tk.Tk()
    app = StudentManagementApp(root)
    root.mainloop()