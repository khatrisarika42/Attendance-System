import os
import zipfile

# Define the folder structure and file contents
project_files = {
    "attendance_system/app.py": '''from flask import Flask
from controllers.attendance_controller import attendance_bp
from models.attendance_model import init_db
import os

# Create Flask app and tell it to look in the 'views' folder for HTML
app = Flask(__name__, template_folder='views', static_folder='static')

# Register our controller routes
app.register_blueprint(attendance_bp)

# Required for flashing messages between requests
app.secret_key = 'attendance-secret-key'

# Ensure database directory exists and initialize DB
if not os.path.exists('database'):
    os.makedirs('database')

init_db()  # Create tables

if __name__ == '__main__':
    app.run(debug=True)
''',
    "attendance_system/models/__init__.py": "",
    "attendance_system/models/attendance_model.py": '''import sqlite3
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
    cursor.execute(\'\'\'
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            department TEXT NOT NULL
        )
    \'\'\')
    
    # Create Attendance Table
    cursor.execute(\'\'\'
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            status TEXT NOT NULL,
            FOREIGN KEY (employee_id) REFERENCES employees (id)
        )
    \'\'\')
    
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
    records = conn.execute(\'\'\'
        SELECT attendance.id, employees.name, employees.department, attendance.date, attendance.status
        FROM attendance
        JOIN employees ON attendance.employee_id = employees.id
        ORDER BY attendance.date DESC
    \'\'\').fetchall()
    conn.close()
    return records
''',
    "attendance_system/controllers/__init__.py": "",
    "attendance_system/controllers/attendance_controller.py": '''from flask import Blueprint, render_template, request, redirect, url_for, flash
from models.attendance_model import (
    get_all_employees, add_employee, 
    get_attendance_records, mark_attendance
)

# Create a Blueprint for our routes
attendance_bp = Blueprint('attendance', __name__)

@attendance_bp.route('/')
def index():
    """Renders the Home Page (View)"""
    return render_template('index.html')

@attendance_bp.route('/employees', methods=['GET', 'POST'])
def employees():
    """Handles viewing and adding employees"""
    if request.method == 'POST':
        name = request.form.get('name')
        department = request.form.get('department')
        
        # Save to database (Model)
        if name and department:
            add_employee(name, department)
            flash('Employee added successfully!', 'success')
        else:
            flash('Please fill in both fields.', 'error')
        return redirect(url_for('attendance.employees'))

    # Fetch all employees (Model) and pass to HTML (View)
    all_employees = get_all_employees()
    return render_template('employees.html', employees=all_employees)

@attendance_bp.route('/attendance', methods=['GET', 'POST'])
def attendance():
    """Handles viewing and marking attendance"""
    if request.method == 'POST':
        employee_id = request.form.get('employee_id')
        date = request.form.get('date')
        status = request.form.get('status')
        
        if employee_id and date and status:
            mark_attendance(employee_id, date, status)
            flash('Attendance marked successfully!', 'success')
        else:
            flash('Please fill in all fields.', 'error')
        return redirect(url_for('attendance.attendance'))
        
    all_employees = get_all_employees()
    records = get_attendance_records()
    return render_template('attendance.html', employees=all_employees, records=records)
''',
    "attendance_system/views/index.html": '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Attendance System</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
</head>
<body>
    <nav class="navbar">
        <a class="brand" href="/">Attendance System</a>
        <div class="nav-links">
            <a href="/" class="active">Home</a>
            <a href="/employees">Employees</a>
            <a href="/attendance">Attendance</a>
        </div>
    </nav>

    <div class="container">
        <h1>Attendance Management System</h1>
        <p>Welcome, Admin! Choose an option below to get started:</p>

        <div class="cards">
            <div class="card">
                <h2>Manage Employees</h2>
                <p>Add new employees and view everyone in the system.</p>
                <a href="/employees">Go to Employees</a>
            </div>
            <div class="card">
                <h2>Mark Attendance</h2>
                <p>Record who was present or absent and view past records.</p>
                <a href="/attendance">Go to Attendance</a>
            </div>
        </div>
    </div>
</body>
</html>
''',
    "attendance_system/views/employees.html": '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Employees - Attendance System</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
</head>
<body>
    <nav class="navbar">
        <a class="brand" href="/">Attendance System</a>
        <div class="nav-links">
            <a href="/">Home</a>
            <a href="/employees" class="active">Employees</a>
            <a href="/attendance">Attendance</a>
        </div>
    </nav>

    <div class="container">
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% for category, message in messages %}
                <div class="flash {{ category }}">{{ message }}</div>
            {% endfor %}
        {% endwith %}

        <h1>Employees</h1>

        <div class="form-box">
            <h2>Add Employee</h2>
            <form action="/employees" method="POST">
                <label for="name">Employee Name</label>
                <input type="text" id="name" name="name" placeholder="e.g. Priya Sharma" required>

                <label for="department">Department</label>
                <input type="text" id="department" name="department" placeholder="e.g. Computer Science" required>

                <button type="submit">Add Employee</button>
            </form>
        </div>

        <div class="table-box">
            <h2>All Employees</h2>
            {% if employees %}
            <table>
                <tr>
                    <th>ID</th>
                    <th>Name</th>
                    <th>Department</th>
                </tr>
                {% for emp in employees %}
                <tr>
                    <td>{{ emp.id }}</td>
                    <td>{{ emp.name }}</td>
                    <td>{{ emp.department }}</td>
                </tr>
                {% endfor %}
            </table>
            {% else %}
            <p class="empty">No employees yet. Add one using the form above.</p>
            {% endif %}
        </div>

        <br>
        <a href="/">Back to Home</a>
    </div>
</body>
</html>
''',
    "attendance_system/views/attendance.html": '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Attendance - Attendance System</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
</head>
<body>
    <nav class="navbar">
        <a class="brand" href="/">Attendance System</a>
        <div class="nav-links">
            <a href="/">Home</a>
            <a href="/employees">Employees</a>
            <a href="/attendance" class="active">Attendance</a>
        </div>
    </nav>

    <div class="container">
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% for category, message in messages %}
                <div class="flash {{ category }}">{{ message }}</div>
            {% endfor %}
        {% endwith %}

        <h1>Mark Attendance</h1>

        <div class="form-box">
            <h2>Daily Attendance</h2>
            {% if employees %}
            <form action="/attendance" method="POST">
                <label for="employee_id">Employee</label>
                <select id="employee_id" name="employee_id">
                    {% for emp in employees %}
                    <option value="{{ emp.id }}">{{ emp.name }} ({{ emp.department }})</option>
                    {% endfor %}
                </select>

                <label for="date">Date</label>
                <input type="date" id="date" name="date" required>

                <label for="status">Status</label>
                <select id="status" name="status">
                    <option value="Present">Present</option>
                    <option value="Absent">Absent</option>
                </select>

                <button type="submit">Submit Attendance</button>
            </form>
            {% else %}
            <p class="empty">No employees yet. Add employees first from the Employees page.</p>
            {% endif %}
        </div>

        <div class="table-box">
            <h2>Attendance Records</h2>
            {% if records %}
            <table>
                <tr>
                    <th>ID</th>
                    <th>Employee Name</th>
                    <th>Department</th>
                    <th>Date</th>
                    <th>Status</th>
                </tr>
                {% for record in records %}
                <tr>
                    <td>{{ record.id }}</td>
                    <td>{{ record.name }}</td>
                    <td>{{ record.department }}</td>
                    <td>{{ record.date }}</td>
                    <td><span class="{{ 'badge present' if record.status == 'Present' else 'badge absent' }}">{{ record.status }}</span></td>
                </tr>
                {% endfor %}
            </table>
            {% else %}
            <p class="empty">No attendance records yet.</p>
            {% endif %}
        </div>

        <br>
        <a href="/">Back to Home</a>
    </div>
</body>
</html>
''',
    "attendance_system/static/style.css": '''body {
    font-family: Arial, sans-serif;
    background-color: #eef2f5;
    margin: 0;
    padding: 0;
}

/* Top navigation bar */
.navbar {
    background-color: #2c3e50;
    padding: 15px 30px;
    display: flex;
    align-items: center;
    justify-content: space-between;
}
.navbar .brand {
    color: white;
    font-size: 20px;
    font-weight: bold;
    text-decoration: none;
}
.navbar .nav-links a {
    color: #ecf0f1;
    text-decoration: none;
    margin-left: 20px;
    padding: 8px 14px;
    border-radius: 4px;
}
.navbar .nav-links a:hover {
    background-color: #34495e;
}
.navbar .nav-links a.active {
    background-color: #3498db;
}

.container {
    max-width: 900px;
    margin: 30px auto;
    padding: 0 20px;
}

h1 {
    color: #2c3e50;
    margin-top: 0;
}
h2 {
    color: #2c3e50;
}

/* Success / error messages after a form is submitted */
.flash {
    padding: 12px 16px;
    border-radius: 4px;
    margin-bottom: 20px;
}
.flash.success {
    background-color: #d4edda;
    color: #155724;
    border: 1px solid #c3e6cb;
}
.flash.error {
    background-color: #f8d7da;
    color: #721c24;
    border: 1px solid #f5c6cb;
}

/* Cards on the home page */
.cards {
    display: flex;
    gap: 20px;
    margin-top: 30px;
}
.card {
    flex: 1;
    background: white;
    border-radius: 8px;
    padding: 30px;
    text-align: center;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}
.card p {
    color: #7f8c8d;
}
.card a {
    display: inline-block;
    margin-top: 10px;
    padding: 10px 20px;
    background-color: #3498db;
    color: white;
    text-decoration: none;
    border-radius: 4px;
}
.card a:hover {
    background-color: #2980b9;
}

/* Forms */
.form-box {
    background: white;
    padding: 20px;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    margin-bottom: 30px;
}
.form-box label {
    display: block;
    margin: 10px 0 5px;
    color: #2c3e50;
    font-weight: bold;
    font-size: 14px;
}
.form-box input,
.form-box select {
    width: 100%;
    padding: 10px;
    border: 1px solid #ccc;
    border-radius: 4px;
    box-sizing: border-box;
    font-size: 14px;
}
.form-box button {
    margin-top: 15px;
    background-color: #27ae60;
    color: white;
    border: none;
    padding: 10px 24px;
    border-radius: 4px;
    font-size: 15px;
    cursor: pointer;
}
.form-box button:hover {
    background-color: #219653;
}

/* Tables */
.table-box {
    background: white;
    padding: 20px;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}
table {
    width: 100%;
    border-collapse: collapse;
}
th,
td {
    padding: 10px;
    text-align: left;
    border-bottom: 1px solid #e0e0e0;
}
th {
    background-color: #3498db;
    color: white;
}
tr:nth-child(even) {
    background-color: #f8f9fa;
}

/* Attendance status badges */
.badge {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 12px;
    font-size: 13px;
    font-weight: bold;
}
.badge.present {
    background-color: #d4edda;
    color: #155724;
}
.badge.absent {
    background-color: #f8d7da;
    color: #721c24;
}

.empty {
    color: #7f8c8d;
    text-align: center;
    padding: 20px;
}
'''
}

print("Creating folder structure and files...")
# Create directories and write files
for filepath, content in project_files.items():
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")

# Create a placeholder for the database directory
os.makedirs("attendance_system/database", exist_ok=True)

# Zip the directory
zip_filename = "attendance_system.zip"
print(f"Zipping into {zip_filename}...")
with zipfile.ZipFile(zip_filename, "w", zipfile.ZIP_DEFLATED) as zipf:
    for root, dirs, files in os.walk("attendance_system"):
        for file in files:
            file_path = os.path.join(root, file)
            arcname = os.path.relpath(file_path, ".")
            zipf.write(file_path, arcname)

print("Done! You should now see 'attendance_system.zip' and the 'attendance_system' folder in your directory.")
