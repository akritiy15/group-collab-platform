from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash

from app.models import User
from app.extensions import db
from sqlalchemy.exc import IntegrityError

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/")
def index():
    return render_template("index.html")


# ---------------- REGISTER ----------------
@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        # ✅ CHECK IF EMAIL EXISTS
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("Email already registered. Please log in instead.", "error")
            return redirect(url_for("auth.register"))

        hashed_password = generate_password_hash(password)

        user = User(
            username=username,
            email=email,
            password=hashed_password
        )

        try:
            db.session.add(user)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            flash("Username already exists 😅 Please choose another one.", "error")
            return redirect(url_for("auth.register"))

        flash("Account created successfully! Please log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("register.html")


# ---------------- LOGIN ----------------
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for("groups.create_group"))

        flash("Invalid email or password", "error")
        return redirect(url_for("auth.login"))

    return render_template("login.html")


# ---------------- LOGOUT ----------------
@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))