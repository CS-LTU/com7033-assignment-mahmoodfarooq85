# Importing necessary libraries
import sqlite3
import pandas as pd
from flask import Flask, render_template, request
from werkzeug.security import generate_password_hash, check_password_hash
import logging

# Enable logging
logging.basicConfig(filename='app.log', level=logging.INFO)

# Initialising the Flask web application
app = Flask(__name__)
DB_NAME = 'users.db'

# This function to create database and users table
def init_db():
    # Creating the database and users table if they do not exist
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()

        # --- Users table (for login/registration) ---
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL
            )
        """)

        # --- Patients table (for CRUD demo) ---
        # This simple table will store a patient's name, age, and condition.
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS patients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                age INTEGER NOT NULL,
                condition TEXT NOT NULL
            )
        """)

        conn.commit()

# Route for home page
@app.route("/")
def home():
    return render_template("home.html")


# Route for about page
@app.route("/about")
def about():
    return render_template("about.html")


# Route for register page
@app.route('/register', methods=['GET', 'POST'])
def register():
    """
    This function handles the register page.
    GET -> show empty form
    POST -> read the form, validate, save user, show a message
    """
    message = "" # default message is empty

    if request.method == 'POST':
        # 1️⃣ Read values from the form
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        role = request.form.get('role', '').strip()

        # 2️⃣ Basic validation
        if not username or not password or not confirm_password or not role:
            message = "Please fill in all fields and select a role."
        elif password != confirm_password:
            message = "Passwords do not match. Please try again."
        else:
            # 3️⃣ Hash password and insert user
            hashed_password = generate_password_hash(password)
            try:
                with sqlite3.connect(DB_NAME) as conn:
                    cursor = conn.cursor()
                    cursor.execute(
                        "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                        (username, hashed_password, role),
                    )
                    conn.commit()
                message = f"User '{username}' registered successfully as {role.capitalize()}!"
            except sqlite3.IntegrityError:
                message = "That username is already taken. Please choose another."

    # 4️⃣ Always render the register page with message
    return render_template('register.html', message=message)


# Route for login page
@app.route("/login", methods=["GET", "POST"])
def login():
    """
    This function handles the login page.
    - GET -> show empty login form
    - POST -> check username + password, then send to correct dashboard
    """
    message = "" # default: no message

    if request.method == "POST":
        # 1) Read values from the form
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        if not username or not password:
            message = "Please enter both username and password."
        else:
            # 2) Look up this user in the database
            with sqlite3.connect(DB_NAME) as conn:
                cur = conn.cursor()
                cur.execute(
                    "SELECT password_hash, role FROM users WHERE username = ?",
                    (username,)
                )
                row = cur.fetchone()

            if row is None:
                # No such username
                message = "Invalid username or password."
            else:
                stored_hash, role = row

                # 3) Check the password against the stored hash
                if check_password_hash(stored_hash, password):
                    # 4) Send to doctor or patient dashboard
                    if role.lower() == "doctor":
                        return render_template("doctor_dashboard.html", username=username)
                    elif role.lower() == "patient":
                        return render_template("patient_dashboard.html", username=username)
                    else:
                        message = "Unknown role. Please contact admin."
                else:
                    message = "Invalid username or password."

    # If GET request or there was an error, show the login page again
    return render_template("login.html", message=message)
# Route for logging out the user
@app.route("/logout")
def logout():
    # Show the login page again with a friendly message
    message = "You have been logged out successfully."
    return render_template("login.html", message=message)
# Route for patients page (simple placeholder for now)
@app.route("/patients", methods=["GET", "POST"])
def patients():
    """
    This route handles the Patients page.

    - GET -> show the form and the list of existing patients
    - POST -> read the form, validate it, save a new patient, then show a message
    """
    message = "" # default: no message

    # --- 1) If the user submitted the 'Add Patient' form ---
    if request.method == "POST":
        # Read values from the form (and strip spaces from start/end)
        name = request.form.get("name", "").strip()
        age_raw = request.form.get("age", "").strip()
        condition = request.form.get("condition", "").strip()

        # --- 2) Basic validation on the form input ---
        if not name or not age_raw or not condition:
            # If any field is empty, ask the user to fill them all
            message = "Please fill in all fields."
        else:
            try:
                # Try to convert age to an integer
                age = int(age_raw)

                # Age should be a positive number
                if age <= 0:
                    raise ValueError
            except ValueError:
                # If conversion fails or age <= 0, show an error
                message = "Age must be a positive number."
            else:
                # --- 3) Save the new patient into the database ---
                with sqlite3.connect(DB_NAME) as conn:
                    cursor = conn.cursor()
                    cursor.execute(
                        "INSERT INTO patients (name, age, condition) VALUES (?, ?, ?)",
                        (name, age, condition),
                    )
                    conn.commit()

                # Friendly success message
                message = f"Patient '{name}' added successfully."

    # --- 4) For both GET and POST: load all patients from the database ---
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, age, condition FROM patients")
        patients = cursor.fetchall()

    # --- 5) Show the template, sending the patient list and any message ---
    return render_template("patients.html", patients=patients, message=message)


# Route to UPDATE an existing patient
@app.route("/patients/update", methods=["POST"])
def update_patient():
    """Update an existing patient record."""
    message = ""

    # 1) Read values from the update form
    patient_id = request.form.get("id", "").strip()
    name = request.form.get("name", "").strip()
    age = request.form.get("age", "").strip()
    condition = request.form.get("condition", "").strip()

    # 2) Basic validation
    if not patient_id or not name or not age or not condition:
        message = "Please fill in all fields for update."
    else:
        try:
            id_int = int(patient_id)
            age_int = int(age)

            if id_int <= 0 or age_int <= 0:
                message = "ID and age must be positive numbers."
            else:
                # 3) Try to update the record in the database
                with sqlite3.connect(DB_NAME) as conn:
                    cursor = conn.cursor()
                    cursor.execute(
                        "UPDATE patients SET name = ?, age = ?, condition = ? WHERE id = ?",
                        (name, age_int, condition, id_int),
                    )

                    # rowcount tells us if a row was actually updated
                    if cursor.rowcount == 0:
                        message = f"No patient found with ID {id_int}."
                    else:
                        conn.commit()
                        message = f"Patient {id_int} updated successfully."
        except ValueError:
            message = "ID and age must be numbers."

    # 4) Re-read all patients and show the page again
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, age, condition FROM patients ORDER BY id")
        patients = cursor.fetchall()

    return render_template("patients.html", message=message, patients=patients)

# Route to DELETE an existing patient
@app.route("/patients/delete", methods=["POST"])
def delete_patient():
    """Delete a patient record."""
    message = ""

    # 1) Read the patient ID from the delete form
    patient_id = request.form.get("id", "").strip()

    if not patient_id:
        message = "Please provide a patient ID to delete."
    else:
        try:
            id_int = int(patient_id)

            if id_int <= 0:
                message = "ID must be a positive number."
            else:
                with sqlite3.connect(DB_NAME) as conn:
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM patients WHERE id = ?", (id_int,))

                    if cursor.rowcount == 0:
                        message = f"No patient found with ID {id_int}."
                    else:
                        conn.commit()
                        message = f"Patient {id_int} deleted successfully."
        except ValueError:
            message = "ID must be a number."

    # 2) Re-read all patients and show the page again
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, age, condition FROM patients ORDER BY id")
        patients = cursor.fetchall()

    return render_template("patients.html", message=message, patients=patients)

@app.route("/show_data")
def show_data():
    # 1) Read the CSV file into a pandas DataFrame
    df = pd.read_csv("stroke_data.csv")

    # 2) Take only the first 20 rows so the table is small
    small_df = df.head(20)

    # 3) Turn the DataFrame into an HTML table
    table_html = small_df.to_html(
        classes="data-table", # CSS class name (for styling later)
        index=False # Do not show the index column
    )

    # 4) Send the table HTML into our data.html template as "table"
    return render_template("data.html", table=table_html)

# ERROR HANDLING ROUTES
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template("500.html"), 500


# Run the Flask app
if __name__ == "__main__":
    init_db() # create the database if not exists
    app.run(debug=True)
    # -------------------------
# ERROR HANDLING ROUTES
# -------------------------

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template("500.html"), 500


