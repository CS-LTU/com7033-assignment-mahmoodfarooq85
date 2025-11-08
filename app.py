# Importing necessary libraries
from flask import Flask, render_template, request
import pandas as pd
import sqlite3
from werkzeug.security import generate_password_hash

# Initialising the Flask web application
app = Flask(__name__)

# Giving Database file name
DB_NAME = "users.db"

# Next step is function to create database and users table
def init_db():
    # Creating the database and users table if they do not exist
    with sqlite3.connect(DB_NAME) as conn:
        cur = conn.cursor()
        cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
        """)