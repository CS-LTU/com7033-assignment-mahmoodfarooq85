# Importing necessary libraries
import os
import sqlite3
import logging
from math import ceil
from datetime import datetime
from functools import wraps

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
)
from werkzeug.security import generate_password_hash, check_password_hash

# Optional: pandas for CSV handling
import pandas as pd

# MongoDB helper (from your mongo.py)
from mongo import db, users_collection
patients_collection = db["patients"]

# ---------- Settings ----------
DB_NAME = "users.db"
DATA_CSV = "stroke_data.csv" # must exist in project folder
PAGE_SIZE = 50 # rows per CSV page

# ---------- App + Logging ----------
app = Flask(__name__)
app.secret_key = "change_this_to_any_random_secret_string"
app.config["HOSPITAL_NAME"] = "CityCare Hospital"

logging.basicConfig(filename="app.log", level=logging.INFO)


@app.context_processor
def inject_globals():
    # So templates can use {{ HOSPITAL_NAME }}
    return {"HOSPITAL_NAME": app.config.get("HOSPITAL_NAME", "Hospital")}


# ---------- Auth helper ----------
def login_required(role=None):
    """
    - If user is not logged in -> redirect to login
    - If role is given and doesn't match session["role"] -> deny access
    """
    def wrapper(fn):
        @wraps(fn)
        def decorated(*args, **kwargs):
            if not session.get("username"):
                flash("You must be logged in to access that page.", "error")
                return redirect(url_for("login"))

            if role and session.get("role") != role:
                flash("Access denied: insufficient permissions.", "error")
                return redirect(url_for("login"))

            return fn(*args, **kwargs)
        return decorated
    return wrapper


# ---------- Database Setup ----------
def init_db():
    os.makedirs(os.path.dirname(os.path.abspath(DB_NAME)), exist_ok=True)
    with sqlite3.connect(DB_NAME) as conn:
        cur = conn.cursor()

        # Users table
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

        # Patients table
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


# ---------- Public Pages ----------
@app.route("/")
def home():
    return render_template("home.html")


@app.route("/about")
def about():
    return render_template("about.html")


# ---------- Authentication ----------
@app.route("/register", methods=["GET", "POST"])
def register():
    message = ""

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")
        role = request.form.get("role", "")

        if not username or not password or not confirm or not role:
            message = "Please fill all fields."
        elif password != confirm:
            message = "Passwords do not match."
        else:
            try:
                pwd_hash = generate_password_hash(password)

                # SQLite
                with sqlite3.connect(DB_NAME) as conn:
                    cur = conn.cursor()
                    cur.execute(
                        "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                        (username, pwd_hash, role),
                    )
                    conn.commit()

                # Optional: also mirror into MongoDB
                try:
                    users_collection.insert_one(
                        {
                            "username": username,
                            "password_hash": pwd_hash,
                            "role": role,
                            "created_at": datetime.utcnow(),
                        }
                    )
                except Exception as e:
                    app.logger.warning(f"Mongo user insert failed for {username}: {e}")

                message = f"User '{username}' registered successfully!"

            except sqlite3.IntegrityError:
                message = "Username already exists."

    return render_template("register.html", message=message)


@app.route("/login", methods=["GET", "POST"])
def login():
    message = ""
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if not username or not password:
            message = "Please fill in all fields."
            return render_template("login.html", message=message)

        with sqlite3.connect(DB_NAME) as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT password_hash, role FROM users WHERE username = ?",
                (username,),
            )
            row = cur.fetchone()

        if row and check_password_hash(row[0], password):
            role = row[1]
            session["username"] = username
            session["role"] = role

            if role == "doctor":
                return redirect(url_for("doctor_dashboard"))
            elif role == "patient":
                return redirect(url_for("patient_dashboard"))
            else:
                return redirect(url_for("home"))

        message = "Invalid username or password."

    return render_template("login.html", message=message)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# ---------- Dashboards ----------
@app.route("/doctor_dashboard")
@login_required(role="doctor")
def doctor_dashboard():
    return render_template("doctor_dashboard.html")


@app.route("/patient_dashboard")
@login_required(role="patient")
def patient_dashboard():
    return render_template("patient_dashboard.html")


# ---------- Patients CRUD + CSV ----------
@app.route("/patients", methods=["GET", "POST"])
@login_required(role="doctor")
def patients():
    """
    - POST: Add new patient to SQLite (main DB) + MongoDB (second DB).
    - GET : Show
        * SQLite patients with update/delete
        * stroke_data.csv rows with pagination + CRUD.
    """
    message = ""

    # ----- Add Patient (SQLite + Mongo) -----
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        age_s = request.form.get("age", "").strip()
        cond = request.form.get("condition", "").strip()

        if not name or not age_s or not cond:
            message = "Fill all fields."
        else:
            try:
                age = int(age_s)
                if age <= 0:
                    message = "Age must be a positive number."
                else:
                    # SQLite insert
                    with sqlite3.connect(DB_NAME) as conn:
                        cur = conn.cursor()
                        cur.execute(
                            "INSERT INTO patients (name, age, condition) VALUES (?, ?, ?)",
                            (name, age, cond),
                        )
                        conn.commit()
                        patient_id = cur.lastrowid # get generated ID

                    # Mirror into Mongo with same id
                    try:
                        patients_collection.insert_one(
                            {
                                "id": patient_id,
                                "name": name,
                                "age": age,
                                "condition": cond,
                                "created_at": datetime.utcnow(),
                                "added_by": session.get("username"),
                                "source": "web_form",
                            }
                        )
                    except Exception as e:
                        app.logger.warning(
                            f"Mongo patient insert failed for {name}: {e}"
                        )

                    message = f"Patient '{name}' added."
            except ValueError:
                message = "Age must be a number."

    # ----- Read patients from SQLite -----
    with sqlite3.connect(DB_NAME) as conn:
        cur = conn.cursor()
        cur.execute("SELECT id, name, age, condition FROM patients ORDER BY id ASC")
        patients_list = cur.fetchall()

    # ----- CSV pagination -----
    page = int(request.args.get("page", 1))
    if page < 1:
        page = 1

    csv_rows = []
    total_rows = 0

    try:
        df = pd.read_csv(DATA_CSV).fillna("")
        total_rows = len(df)

        # keep true index for safe updates/deletes
        df = df.reset_index(drop=False).rename(columns={"index": "_idx"})

        wanted = [
            "id",
            "gender",
            "age",
            "hypertension",
            "heart_disease",
            "ever_married",
            "work_type",
            "Residence_type",
            "avg_glucose_level",
            "bmi",
            "smoking_status",
            "stroke",
        ]
        cols = [c for c in ["_idx"] + wanted if c in df.columns]

        start = (page - 1) * PAGE_SIZE
        end = start + PAGE_SIZE
        page_df = df.loc[start:end - 1, cols]
        csv_rows = page_df.to_dict(orient="records")
    except Exception as e:
        app.logger.exception("Failed to load CSV")
        if not message:
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
        page_size=PAGE_SIZE,
    )


# ----- Patients (SQLite) UPDATE + mirror to Mongo -----
@app.route("/patients/update", methods=["POST"])
@login_required(role="doctor")
def update_patient():
    pid = request.form.get("id", "").strip()
    name = request.form.get("name", "").strip()
    age_s = request.form.get("age", "").strip()
    cond = request.form.get("condition", "").strip()

    if not pid or not name or not age_s or not cond:
        flash("Fill all fields for update.", "error")
        return redirect(url_for("patients"))

    try:
        pid_i = int(pid)
        age_i = int(age_s)
    except ValueError:
        flash("ID and age must be numbers.", "error")
        return redirect(url_for("patients"))

    # SQLite update
    with sqlite3.connect(DB_NAME) as conn:
        cur = conn.cursor()
        cur.execute(
            "UPDATE patients SET name = ?, age = ?, condition = ? WHERE id = ?",
            (name, age_i, cond, pid_i),
        )
        conn.commit()

    # Mongo update
    try:
        patients_collection.update_one(
            {"id": pid_i},
            {"$set": {"name": name, "age": age_i, "condition": cond}},
            upsert=True,
        )
    except Exception as e:
        app.logger.warning(f"Mongo patient update failed (id={pid_i}): {e}")

    flash(f"Patient {pid_i} updated.", "success")
    return redirect(url_for("patients"))


# ----- Patients (SQLite) DELETE + mirror to Mongo -----
@app.route("/patients/delete", methods=["POST"])
@login_required(role="doctor")
def delete_patient():
    pid = request.form.get("id", "").strip()

    try:
        pid_i = int(pid)
    except ValueError:
        flash("Invalid patient ID.", "error")
        return redirect(url_for("patients"))

    # SQLite delete
    with sqlite3.connect(DB_NAME) as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM patients WHERE id = ?", (pid_i,))
        conn.commit()

    # Mongo delete
    try:
        patients_collection.delete_one({"id": pid_i})
    except Exception as e:
        app.logger.warning(f"Mongo patient delete failed (id={pid_i}): {e}")

    flash(f"Patient {pid_i} deleted.", "success")
    return redirect(url_for("patients"))


# ----- CSV Update/Delete (by true DataFrame index) -----
@app.post("/patients/stroke/update")
@login_required(role="doctor")
def update_stroke_row():
    try:
        idx = int(request.form.get("row_index", "-1"))
        df = pd.read_csv(DATA_CSV).fillna("")
        if idx < 0 or idx >= len(df):
            flash(f"Row {idx} not found.", "error")
            return redirect(url_for("patients"))

        for col in [
            "id",
            "gender",
            "age",
            "hypertension",
            "heart_disease",
            "ever_married",
            "work_type",
            "Residence_type",
            "avg_glucose_level",
            "bmi",
            "smoking_status",
            "stroke",
        ]:
            if col in request.form and request.form[col] != "":
                val = request.form[col]
                if col in ["age", "avg_glucose_level", "bmi"]:
                    try:
                        val = float(val)
                    except ValueError:
                        flash(f"Invalid value for {col}.", "error")
                        return redirect(url_for("patients"))
                df.at[idx, col] = val

        df.to_csv(DATA_CSV, index=False)
        flash(f"Row {idx} updated.", "success")
    except Exception as e:
        app.logger.exception("Update error")
        flash(f"Update error: {e}", "error")

    return redirect(url_for("patients"))


@app.post("/patients/stroke/delete")
@login_required(role="doctor")
def delete_stroke_row():
    try:
        idx = int(request.form.get("row_index", "-1"))
        df = pd.read_csv(DATA_CSV).fillna("")
        if idx < 0 or idx >= len(df):
            flash(f"Row {idx} not found.", "error")
            return redirect(url_for("patients"))

        df = df.drop(index=idx).reset_index(drop=True)
        df.to_csv(DATA_CSV, index=False)
        flash(f"Row {idx} deleted.", "success")
    except Exception as e:
        app.logger.exception("Delete error")
        flash(f"Delete error: {e}", "error")

    return redirect(url_for("patients"))


# ---------- Error Pages ----------
@app.errorhandler(404)
def not_found(e):
    return render_template("404.html"), 404


@app.errorhandler(500)
def server_error(e):
    app.logger.error(f"Server error: {e}")
    return render_template("500.html", message="Internal Server Error"), 500


@app.route("/force500")
def force500():
    # If you ever want to demo a 500 page manually
    raise Exception("Simulated crash for demo")


# ---------- Run ----------
if __name__ == "__main__":
    init_db()
    print("Server running at http://127.0.0.1:5000")
    app.run(debug=True)