import os
import sqlite3
from flask_session import Session
from flask import Flask, flash, redirect, render_template, request, session, url_for
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up the database connection
DATABASE = "database.db"

def get_db():
    """Create and return a database connection."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # Enable dictionary-like cursor
    return conn

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/choice", methods=["GET", "POST"])
def choice():
    if request.method == "POST":
        interests = request.form.getlist("interests")
        user_id = session.get("user_id")
        
        if not user_id:
            flash("Please log in to save your interests.")
            return redirect("/login")

        with get_db() as conn:
            conn.execute("DELETE FROM user_interests WHERE user_id = ?", (user_id,))
            conn.executemany("INSERT INTO user_interests (user_id, interest) VALUES (?, ?)", [(user_id, i) for i in interests])
            conn.commit()

        flash("Your interests have been saved!")
        return redirect("/")
    
    return render_template("choice.html")

@app.route("/shorts")
def shorts():
    return render_template("shorts.html")

@app.route("/tech")
def tech():
    return render_template("tech.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        if not username or not password or not confirmation:
            flash("All fields are required.")
            return redirect("/register")

        if password != confirmation:
            flash("Passwords do not match.")
            return redirect("/register")

        hash_pass = generate_password_hash(password)

        with get_db() as conn:
            try:
                conn.execute("INSERT INTO users (username, hash) VALUES (?, ?)", (username, hash_pass))
                conn.commit()
            except sqlite3.IntegrityError:
                flash("Username already exists.")
                return redirect("/register")

        flash("Registered successfully! Please log in.")
        return redirect("/login")
    
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if not username or not password:
            flash("Username and password are required.")
            return redirect("/login")

        with get_db() as conn:
            user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()

        if user is None or not check_password_hash(user["hash"], password):
            flash("Invalid username or password.")
            return redirect("/login")

        session["user_id"] = user["id"]
        flash("Logged in successfully!")
        return redirect("/")
    
    return render_template("login.html")

@app.route("/logout")
def logout():
    """Log user out"""
    session.clear()
    flash("You have been logged out.")
    return redirect("/")

def init_db():
    """Initialize the database with required tables."""
    with get_db() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            hash TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS user_interests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            interest TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        );
        """)
        conn.commit()

if __name__ == "__main__":
    # Initialize the database tables if they don't exist
    init_db()
    app.run(debug=True)
