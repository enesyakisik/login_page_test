import os
from datetime import datetime

from flask import Flask, redirect, render_template, request, session, url_for, flash
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy import create_engine, text
from sqlalchemy.exc import IntegrityError


DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "appdb")
DB_USER = os.getenv("DB_USER", "k8suser")
DB_PASSWORD = os.getenv("DB_PASSWORD", "1qaz2wsx")
DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DATABASE_URL, pool_size=5, max_overflow=2, pool_pre_ping=True)

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-secret-key")


def init_db():
    with engine.begin() as conn:
        conn.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    created_at TIMESTAMP NOT NULL DEFAULT NOW()
                )
                """
            )
        )


@app.before_first_request
def setup():
    init_db()


def current_user():
    user_id = session.get("user_id")
    if not user_id:
        return None
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT id, email, created_at FROM users WHERE id=:id"),
            {"id": user_id},
        ).mappings().first()
    return result


@app.route("/")
def index():
    user = current_user()
    return render_template("index.html", user=user)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        if not email or not password:
            flash("Email and password are required", "error")
            return redirect(url_for("register"))
        password_hash = generate_password_hash(password)
        try:
            with engine.begin() as conn:
                conn.execute(
                    text("INSERT INTO users (email, password_hash, created_at) VALUES (:email, :password, :created_at)"),
                    {"email": email, "password": password_hash, "created_at": datetime.utcnow()},
                )
            flash("Registration successful. Please log in.", "success")
            return redirect(url_for("login"))
        except IntegrityError:
            flash("Email already registered", "error")
            return redirect(url_for("register"))
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        with engine.connect() as conn:
            user = conn.execute(
                text("SELECT id, email, password_hash FROM users WHERE email=:email"),
                {"email": email},
            ).mappings().first()
        if not user or not check_password_hash(user["password_hash"], password):
            flash("Invalid email or password", "error")
            return redirect(url_for("login"))
        session["user_id"] = user["id"]
        flash("Logged in successfully", "success")
        return redirect(url_for("dashboard"))
    return render_template("login.html")


@app.route("/dashboard")
def dashboard():
    user = current_user()
    if not user:
        flash("Please log in to continue", "error")
        return redirect(url_for("login"))
    return render_template("dashboard.html", user=user)


@app.route("/logout")
def logout():
    session.pop("user_id", None)
    flash("Logged out", "success")
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=True)
