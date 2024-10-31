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
