import sqlite3
import os

# Path to our database
DB_PATH = os.path.join('database', 'attendance.db')

def get_db_connection():
    """Connects to the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Allows us to access columns by name
    return conn

def init_db():
    """Creates the tables if they don't exist."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create Employees Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            department TEXT NOT NULL
        )
    ''')
    
    # Create Attendance Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            status TEXT NOT NULL,
            FOREIGN KEY (employee_id) REFERENCES employees (id)
        )
    ''')
    
    conn.commit()
    conn.close()

def add_employee(name, department):
    """Inserts a new employee into the database."""
    conn = get_db_connection()
    conn.execute('INSERT INTO employees (name, department) VALUES (?, ?)', (name, department))
    conn.commit()
    conn.close()

def get_all_employees():
    """Fetches all employees."""
    conn = get_db_connection()
    employees = conn.execute('SELECT * FROM employees').fetchall()
    conn.close()
    return employees

def mark_attendance(employee_id, date, status):
    """Inserts an attendance record."""
    conn = get_db_connection()
    conn.execute('INSERT INTO attendance (employee_id, date, status) VALUES (?, ?, ?)', 
                 (employee_id, date, status))
    conn.commit()
    conn.close()

def get_attendance_records():
    """Fetches attendance records joined with employee names."""
    conn = get_db_connection()
    records = conn.execute('''
        SELECT attendance.id, employees.name, employees.department, attendance.date, attendance.status
        FROM attendance
        JOIN employees ON attendance.employee_id = employees.id
        ORDER BY attendance.date DESC
    ''').fetchall()
    conn.close()
    return records
