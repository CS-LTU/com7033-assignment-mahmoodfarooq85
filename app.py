# Importing necessary libraries
from flask import Flask, render_template, request
import pandas as pd
import sqlite3
from werkzeug.security import generate_password_hash

# Initialising the Flask web application
app = Flask(__name__)

# Giving Database file name
DB_NAME = "users.db"

# Function to create database and users table
def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL
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
@app.route("/register", methods=["GET", "POST"])
def register():
    return render_template("register.html")
@app.route("/show_data")
def show_data():
    # This route will show few rows from stroke_data.csv

    # 1) Read the CSV file into a pandas 
    df = pd.read_csv("stroke_data.csv")

    # 2) only the first 20 rows 
    small_df = df.head(20)

    # 3) Turning the DataFrame into an HTML table
    # classes="data-table" is just a CSS class name (for styling later if I want)
    # index=False hides the left index column (0,1,2,3...)
    table_html = small_df.to_html(classes="data-table", index=False)

    # 4) Send the table HTML into my data.html template as "table"
    return render_template("data.html", table=table_html)

# Run the Flask app
if __name__ == "__main__":
    init_db() # create the database if not exists
    app.run(debug=True)

