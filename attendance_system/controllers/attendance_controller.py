from flask import Blueprint, render_template, request, redirect, url_for, flash
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
