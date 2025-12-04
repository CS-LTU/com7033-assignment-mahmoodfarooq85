Hospital Secure Web App

This is my(mahmood's) project for the Secure Software Development assignment(COM-7033)
I built it using Flask (Python) 

It has Home, About, Register, Login-(After login, Doctor Dashboard, Patient Dashboard, and Patients Data pages).

A new user can register and log in securely(Both as Doctor and a Patient)

Passwords are hashed, not stored in plain text.
Users have roles → Doctor or Patient.
Only Doctors can access and manage the Patients page.
Doctors can Add / Update / Delete patients.
It displays a real medical dataset (stroke_data.csv) this was provided by our teacher.
           And
User accounts are securely stored in SQLite (primary authentication database).
Patient records are stored in MongoDB (demonstrates secure NoSQL usage).
          
Custom 404 and 500 error pages.

Input validation is used to avoid bad data being saved.
It also shows multiple secure development techniques.

  What Security Feature ih has?Listed below,
  
Password hashing using werkzeug.security
Role-based access control (RBAC)
Authentication checks before showing sensitive pages.

Input validation in forms

Session security (logout option)

.gitignore protects sensitive files such as:

users.db
.env
PyCache folders
app.log, cache files
These helps alot in support of security

  It has Unit Testing also.

I write some tests using pytest to check that:

Home page loads,

Login page loads,

Invalid login shows the correct message,

Protected pages redirect when not logged in,

Custom 404 and 500 pages return correct error responses,

To run tests:
python -m pytest - it shows in vs code terminal 
test_app.py::test_home_page PASSED                                                                                                                       
test_app.py::test_login_page PASSED                                                                                                                      
test_app.py::test_invalid_login PASSED                                                                                                                   
test_app.py::test_patients_protected PASSED                                                                                                             
test_app.py::test_404_page PASSED.           

  How to Run the App Locally,
  
  Open the project folder in VS Code
  
  Open the terminal
  
  Run:
  
python app.py (it shows like)

MongoDB connection OK
Server running at http://127.0.0.1:5000
 * Serving Flask app 'app'
 * Debug mode: on
MongoDB connection OK
Server running at http://127.0.0.1:5000
    
