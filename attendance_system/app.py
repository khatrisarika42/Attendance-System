from flask import Flask
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
