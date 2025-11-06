from flask import Flask, render_template, request
import pandas as pd
import sqlite3
from werkzeug.security import generate_password_hash

app = Flask(__name__)
DB_NAME = "users.db"


def init_db():
    # Create the database and users table if they do not exist
    with sqlite3.connect(DB_NAME) as conn:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL
            );
        """)


@app.route("/")
def home():
    return render_template("home.html", title="Home")


@app.route("/about")
def about():
    return render_template("about.html", title="About")


@app.route("/register", methods=["GET", "POST"])
def register():
    message = None

    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"].strip()

        # Simple input validation
        if not username or not password:
            message = "Username and password are required."
        else:
            password_hash = generate_password_hash(password)

            try:
                # Open connection just for this insert, then auto-close
                with sqlite3.connect(DB_NAME) as conn:
                    cur = conn.cursor()
                    cur.execute(
                        "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                        (username, password_hash),
                    )
                message = f"Account created for {username}!"
            except sqlite3.IntegrityError:
                # Username already exists
                message = "That username is already taken. Please choose another."

    return render_template("register.html", title="Register", message=message)


@app.route("/data")
def show_data():
    df = pd.read_csv("stroke_data.csv") # load your stroke dataset
    return df.head().to_html() # show first 5 rows as an HTML table


if __name__ == "__main__":
    init_db() # make sure database + table exist
    app.run(debug=True)
