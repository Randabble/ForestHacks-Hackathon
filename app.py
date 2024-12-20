import os
import sqlite3
from flask_session import Session
from flask import Flask, flash, redirect, render_template, request, session, url_for
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

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

@app.route("/shorts", methods=["GET", "POST"])
def shorts():
    user_id = session.get("user_id")
    if not user_id:
        flash("Please log in to view shorts.")
        return redirect("/login")

    # Select a video to display (e.g., the next video or a random one)
    with get_db() as conn:
        video = conn.execute("SELECT * FROM videos ORDER BY RANDOM() LIMIT 1").fetchone()

        if video:
            # Log the video in watch_history
            conn.execute(
                """
                INSERT INTO watch_history (user_id, video_id, reaction, timestamp)
                VALUES (?, ?, NULL, ?)
                """,
                (user_id, video["id"], datetime.now())
            )
            conn.commit()

    return render_template("shorts.html", video=video)

@app.route("/like_video", methods=["POST"])
def like_video():
    user_id = session.get("user_id")
    if not user_id:
        return {"error": "User not logged in"}, 401

    video_id = request.json.get("video_id")
    if not video_id:
        return {"error": "Video ID is required"}, 400

    with get_db() as conn:
        # Add like reaction in watch_history
        conn.execute(
            """
            INSERT INTO watch_history (user_id, video_id, reaction, timestamp)
            VALUES (?, ?, 1, ?)
            """,
            (user_id, video_id, datetime.now())
        )

        # Increment the like count in the videos table
        conn.execute(
            "UPDATE videos SET likes = likes + 1 WHERE id = ?",
            (video_id,)
        )
        conn.commit()

    return {"message": "Like recorded successfully"}, 200


@app.route("/tech")
def tech():
    return render_template("tech.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        # Ensure fields are filled
        if not username or not password:
            flash("Please provide both username and password.")
            return redirect("/register")

        hash_pass = generate_password_hash(password)

        with get_db() as conn:
            try:
                conn.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, hash_pass))
                conn.commit()
            except sqlite3.IntegrityError:
                flash("Username already exists.")
                return redirect("/register")

        flash("Registered successfully! Please log in.")
        return redirect("/shorts")
    
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
            conn.row_factory = sqlite3.Row  # Ensures results are dictionary-like
            user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()

        # Check if user exists
        if user is None:
            flash("No account found with that username.")
            return redirect("/login")

        # Verify password
        if not check_password_hash(user["password_hash"], password):
            flash("Password does not match the username.")
            return redirect("/login")

        # Log the user in
        session["user_id"] = user["id"]
        flash("Logged in successfully!")
        return redirect("/shorts")  # Redirect to /shorts as per your flow

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
