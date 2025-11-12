# Importing necessary libraries
import os
import sqlite3
import logging
from math import ceil

from flask import Flask, render_template, request, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash

# Optional: pandas for CSV handling
import pandas as pd

# ---------- Settings ----------
DB_NAME = "users.db"
DATA_CSV = "stroke_data.csv" # must exist in the project folder
PAGE_SIZE = 50 # CSV rows per page (tune as you like)

# ---------- App + Logging ----------
app = Flask(__name__)
app.config["HOSPITAL_NAME"] = "CityCare Hospital"

logging.basicConfig(filename="app.log", level=logging.INFO)

@app.context_processor
def inject_globals():
    return {"HOSPITAL_NAME": app.config.get("HOSPITAL_NAME", "Hospital")}

# ---------- DB Bootstrapping ----------
def init_db():
    os.makedirs(os.path.dirname(os.path.abspath(DB_NAME)), exist_ok=True)
    with sqlite3.connect(DB_NAME) as conn:
        cur = conn.cursor()

        # Users table (for register/login)
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL
            )
            """
        )

        # Patients table (CRUD demo)
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS patients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                age INTEGER NOT NULL,
                condition TEXT NOT NULL
            )
            """
        )
        conn.commit()

# ---------- Simple Pages ----------
@app.route("/")
def home():
    return render_template("home.html")

@app.route("/about")
def about():
    return render_template("about.html")

# ---------- Auth (minimal demo) ----------
@app.route("/register", methods=["GET", "POST"])
def register():
    message = ""
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")
        role = request.form.get("role", "").strip()

        if not username or not password or not confirm or not role:
            message = "Please fill in all fields and select a role."
        elif password != confirm:
            message = "Passwords do not match."
        else:
            try:
                with sqlite3.connect(DB_NAME) as conn:
                    cur = conn.cursor()
                    cur.execute(
                        "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                        (username, generate_password_hash(password), role),
                    )
                    conn.commit()
                message = f"User '{username}' registered successfully as {role.capitalize()}!"
            except sqlite3.IntegrityError:
                message = "That username already exists."
    return render_template("register.html", message=message)

@app.route("/login", methods=["GET", "POST"])
def login():
    message = ""
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        if not username or not password:
            message = "Please enter both username and password."
        else:
            with sqlite3.connect(DB_NAME) as conn:
                cur = conn.cursor()
                cur.execute("SELECT password_hash, role FROM users WHERE username = ?", (username,))
                row = cur.fetchone()
            if not row:
                message = "Invalid username or password."
            else:
                stored_hash, role = row
                if check_password_hash(stored_hash, password):
                    # Demo dashboards (templates should exist)
                    if role.lower() == "doctor":
                        return render_template("doctor_dashboard.html", username=username)
                    elif role.lower() == "patient":
                        return render_template("patient_dashboard.html", username=username)
                    else:
                        message = "Unknown role."
                else:
                    message = "Invalid username or password."
    return render_template("login.html", message=message)

@app.route("/logout")
def logout():
    return render_template("login.html", message="You have been logged out successfully.")

# ---------- Patients (DB CRUD + CSV with pagination + row CRUD) ----------
@app.route("/patients", methods=["GET", "POST"])
def patients():
    """
    - POST: Add a new patient to the SQLite DB
    - GET : Render page with:
        * DB patients (with update/delete forms handled by dedicated routes)
        * CSV data (paged) with Update/Delete per row using the true DataFrame index
    """
    message = ""

    # Handle "Add Patient" form (DB)
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        age_str = request.form.get("age", "").strip()
        condition = request.form.get("condition", "").strip()

        if not name or not age_str or not condition:
            message = "Please fill in all fields to add a patient."
        else:
            try:
                age_int = int(age_str)
                if age_int <= 0:
                    message = "Age must be a positive number."
                else:
                    with sqlite3.connect(DB_NAME) as conn:
                        cur = conn.cursor()
                        cur.execute(
                            "INSERT INTO patients (name, age, condition) VALUES (?, ?, ?)",
                            (name, age_int, condition),
                        )
                        conn.commit()
                    message = f"Patient '{name}' added successfully."
            except ValueError:
                message = "Age must be a number."

    # Read DB patients
    with sqlite3.connect(DB_NAME) as conn:
        cur = conn.cursor()
        cur.execute("SELECT id, name, age, condition FROM patients ORDER BY id ASC")
        patients_list = cur.fetchall()

    # CSV pagination
    page = int(request.args.get("page", 1))
    if page < 1:
        page = 1

    csv_rows = []
    total_rows = 0
    try:
        df = pd.read_csv(DATA_CSV).fillna("")
        total_rows = len(df)

        # keep the true index for safe CRUD
        df = df.reset_index(drop=False).rename(columns={"index": "_idx"})

        wanted = [
            "id", "gender", "age", "hypertension", "heart_disease", "ever_married",
            "work_type", "Residence_type", "avg_glucose_level", "bmi",
            "smoking_status", "stroke"
        ]
        cols = ["_idx"] + [c for c in wanted if c in df.columns]

        start = (page - 1) * PAGE_SIZE
        end = start + PAGE_SIZE
        page_df = df.loc[start:end-1, cols]
        csv_rows = page_df.to_dict(orient="records")
    except Exception as e:
        app.logger.exception("Failed to load CSV")
        message = f"Could not load dataset: {e}"

    total_pages = max(1, ceil(total_rows / PAGE_SIZE))

    return render_template(
        "patients.html",
        message=message,
        patients=patients_list,
        csv_rows=csv_rows,
        page=page,
        total_pages=total_pages,
        total_rows=total_rows,
        page_size=PAGE_SIZE
    )

# ----- Patients (DB) Update/Delete -----
@app.route("/patients/update", methods=["POST"])
def update_patient():
    message = ""
    pid = request.form.get("id", "").strip()
    name = request.form.get("name", "").strip()
    age_s = request.form.get("age", "").strip()
    cond = request.form.get("condition", "").strip()

    if not pid or not name or not age_s or not cond:
        message = "Please fill in all fields for update."
    else:
        try:
            pid_i = int(pid)
            age_i = int(age_s)
            if pid_i <= 0 or age_i <= 0:
                message = "ID and age must be positive numbers."
            else:
                with sqlite3.connect(DB_NAME) as conn:
                    cur = conn.cursor()
                    cur.execute(
                        "UPDATE patients SET name = ?, age = ?, condition = ? WHERE id = ?",
                        (name, age_i, cond, pid_i),
                    )
                    if cur.rowcount == 0:
                        message = f"No patient found with ID {pid_i}."
                    else:
                        conn.commit()
                        message = f"Patient {pid_i} updated successfully."
        except ValueError:
            message = "ID and age must be numbers."

    return redirect(url_for("patients", message=message))

@app.route("/patients/delete", methods=["POST"])
def delete_patient():
    message = ""
    pid = request.form.get("id", "").strip()
    if not pid:
        message = "Please provide a patient ID to delete."
    else:
        try:
            pid_i = int(pid)
            if pid_i <= 0:
                message = "ID must be a positive number."
            else:
                with sqlite3.connect(DB_NAME) as conn:
                    cur = conn.cursor()
                    cur.execute("DELETE FROM patients WHERE id = ?", (pid_i,))
                    if cur.rowcount == 0:
                        message = f"No patient found with ID {pid_i}."
                    else:
                        conn.commit()
                        message = f"Patient {pid_i} deleted successfully."
        except ValueError:
            message = "ID must be a number."
    return redirect(url_for("patients", message=message))

# ----- CSV Update/Delete (by true DataFrame index) -----
@app.post("/patients/stroke/update")
def update_stroke_row():
    message = ""
    try:
        idx = int(request.form.get("row_index", "-1"))
        df = pd.read_csv(DATA_CSV).fillna("")
        if idx < 0 or idx >= len(df):
            message = f"Row {idx} not found."
            return redirect(url_for("patients"))

        # Update only provided fields
        for col in ["id","gender","age","hypertension","heart_disease","ever_married",
                    "work_type","Residence_type","avg_glucose_level","bmi",
                    "smoking_status","stroke"]:
            if col in request.form and request.form[col] != "":
                val = request.form[col]
                if col in ["age", "avg_glucose_level", "bmi"]:
                    try:
                        val = float(val)
                    except ValueError:
                        message = f"Invalid value for {col}"
                        return redirect(url_for("patients"))
                df.at[idx, col] = val

        df.to_csv(DATA_CSV, index=False)
        message = f"Row {idx} updated."
    except Exception as e:
        app.logger.exception("Update error")
        message = f"Update error: {e}"
    return redirect(url_for("patients"))

@app.post("/patients/stroke/delete")
def delete_stroke_row():
    message = ""
    try:
        idx = int(request.form.get("row_index", "-1"))
        df = pd.read_csv(DATA_CSV).fillna("")
        if idx < 0 or idx >= len(df):
            message = f"Row {idx} not found."
            return redirect(url_for("patients"))

        df = df.drop(index=idx).reset_index(drop=True)
        df.to_csv(DATA_CSV, index=False)
        message = f"Row {idx} deleted."
    except Exception as e:
        app.logger.exception("Delete error")
        message = f"Delete error: {e}"
    return redirect(url_for("patients"))

# ---------- Run ----------
if __name__ == "__main__":
    init_db()
    print("Server running at http://127.0.0.1:5000")
    app.run(debug=True)