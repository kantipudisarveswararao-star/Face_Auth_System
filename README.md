Student Dashboard Management System
A Flask-based Student Dashboard Management System for managing student information, marks, attendance, subjects, authentication, and academic performance.
1. Project Overview
The Student Dashboard Management System provides separate functionality for administrators and students.
Administrator features
Admin registration and login
Admin dashboard with student count, average marks, and average attendance
Add, edit, view, and delete student records
Manage student marks by subject
Manage student attendance by subject
View student performance
View analytics/performance pages
Manage administrator profile
Student features
Student login
Student dashboard
View academic performance
View subject marks
View attendance information
View profile
Change account password
2. Technologies Used
Python 3
Flask
Flask-SQLAlchemy
MySQL
PyMySQL
Flask-JWT-Extended for JWT-based authentication
Flask-Bcrypt for password hashing
Flask-WTF
python-dotenv
HTML/CSS/Jinja2 for the web interface
3. Project Structure
```text
student\_dashboard/
│
├── app.py
├── config.py
├── extensions.py
├── requirements.txt
├── Creating VENV in Python.txt
├── student\_dashboard.sql
├── .env
│
├── models/
│   ├── \_\_init\_\_.py
│   ├── user.py
│   ├── student.py
│   ├── subject.py
│   ├── marks.py
│   └── attendance.py
│
├── routes/
│   ├── auth.py
│   ├── admin.py
│   └── student.py
│
├── utils/
│   └── decorators.py
│
└── templates/
    ├── base.html
    ├── index.html
    ├── login.html
    ├── register.html
    ├── admin/
    └── student/
```
4. Database
The application uses MySQL with a database named:
```text
student\_dashboard
```
The supplied `student\_dashboard.sql` file creates the following tables:
`users`
`students`
`subjects`
`marks`
`attendance`
Relationships are implemented using foreign keys. Student-related records are configured to cascade when the associated student/user is deleted.
The SQL script also inserts the initial subjects:
Python Programming (`PY101`)
Database Systems (`DB101`)
Web Development (`WD101`)
Data Structures (`DS101`)
Computer Networks (`CN101`)
Software Engineering (`SE101`)
5. Requirements
Install:
Python 3.9 or later
MySQL Server
MySQL Workbench (recommended for database setup)
A web browser
A code editor/IDE such as Visual Studio Code or PyCharm
6. Installation
Step 1: Extract the project
Extract the ZIP file and open the `student\_dashboard` folder in your IDE.
Step 2: Create a virtual environment
Windows PowerShell:
```powershell
python -m venv venv
```
Activate it:
```powershell
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process
.\\venv\\Scripts\\Activate
```
Step 3: Upgrade pip
```powershell
python -m pip install --upgrade pip
```
Step 4: Install dependencies
```powershell
pip install -r requirements.txt
```
> \*\*Note:\*\* `models/user.py` imports `UserMixin` from `flask\_login`. If your environment reports `ModuleNotFoundError: No module named 'flask\_login'`, install the missing dependency with `pip install Flask-Login`. The current authentication flow itself uses Flask-JWT-Extended.
7. Database Setup
Start MySQL Server.
Open MySQL Workbench.
Open `student\_dashboard.sql`.
Execute the complete SQL script.
Confirm that the `student\_dashboard` database and its tables have been created.
8. Environment Configuration
The application reads database and security configuration from the `.env` file.
Example structure:
```env
SECRET\_KEY=your\_secret\_key
JWT\_SECRET\_KEY=your\_jwt\_secret
DATABASE\_USER=your\_mysql\_username
DATABASE\_PASSWORD=your\_mysql\_password
DATABASE\_HOST=localhost
DATABASE\_NAME=student\_dashboard
```
Security note
Do not commit real passwords, production secret keys, API keys, or other sensitive credentials to GitHub or another public repository. Use your own local `.env` file and add `.env` to `.gitignore`.
9. Run the Application
After activating the virtual environment and configuring MySQL:
```powershell
python app.py
```
The Flask development server will start. Open the local address displayed in the terminal, normally:
```text
http://127.0.0.1:5000/
```
10. Application Workflow
Admin workflow
```text
Home
  ↓
Register / Login
  ↓
Admin Dashboard
  ├── Manage Students
  │     ├── Add Student
  │     ├── Edit Student
  │     └── Delete Student
  ├── Manage Marks
  ├── Manage Attendance
  ├── Performance
  ├── Analytics
  └── Profile
```
Student workflow
```text
Login
  ↓
Student Dashboard
  ├── View Performance
  ├── View Marks
  ├── View Attendance
  └── Profile / Change Password
```
11. Authentication and Security
The application uses:
Flask-Bcrypt to hash user passwords before storing them.
Flask-JWT-Extended for authentication tokens.
JWT cookies to maintain authenticated sessions.
Role-based access control for administrator and student pages.
`role\_required()` to prevent users from accessing pages intended for another role.
Unauthorized users are prevented from accessing protected dashboard routes.
12. Main Routes
Public routes
```text
/
 /login
 /register
 /logout
```
Admin routes
```text
/admin/dashboard
/admin/students
/admin/students/add
/admin/students/edit/<student\_id>
/admin/students/delete/<student\_id>
/admin/performance
/admin/marks/<student\_id>
/admin/marks/edit/<student\_id>/<subject\_id>
/admin/attendance/<student\_id>
/admin/attendance/edit/<student\_id>/<subject\_id>
```
Student routes
```text
/student/dashboard
/student/performance
/student/profile
```
13. Data Model
The core database relationships are:
```text
User
 │
 └── Student
       ├── Marks ────── Subject
       └── Attendance ─ Subject
```
A user can have a student record when the user's role is `student`. Each student can have marks and attendance records associated with individual subjects.
14. Marks and Attendance
Marks
Marks are stored for each student and subject. A unique constraint prevents duplicate marks records for the same student-subject combination.
Attendance
Attendance stores:
Total classes
Attended classes
The application calculates attendance percentage as:
```text
Attendance Percentage =
(Attended Classes / Total Classes) × 100
```
The application also validates that attended classes cannot exceed total classes.
15. Troubleshooting
MySQL connection error
Check:
MySQL Server is running.
Database name is correct.
MySQL username and password are correct.
`DATABASE\_HOST` is correct.
The `student\_dashboard` database has been created.
Module not found error
Activate the virtual environment and run:
```powershell
pip install -r requirements.txt
```
For the `flask\_login` import specifically:
```powershell
pip install Flask-Login
```
Port already in use
Stop the other Flask/application process using the port, or configure the application to use another available port.
Login does not work
Confirm that:
The database is connected.
A user has been registered.
The user exists in the `users` table.
The password is correct.
The Flask application is running without database errors.
16. Development Notes
This project is configured for local development and uses Flask's development server with:
```python
app.run(debug=True)
```
For production deployment, debug mode should be disabled and a production-grade WSGI server and secure HTTPS configuration should be used.
17. Author / Project
Project: Student Dashboard Management System  
Application Type: Web Application  
Backend: Python Flask  
Database: MySQL  
Authentication: JWT + Bcrypt  
Interface: HTML/Jinja2
18. License
This project is intended for academic/development use. Add an appropriate license if the software is distributed or reused outside the original project.
