from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from app.models import User, Group, GroupMember
from app.extensions import db

auth_bp = Blueprint("auth", __name__)

# -------------------- LANDING PAGE --------------------
@auth_bp.route("/")
def index():
    return render_template("index.html")


# -------------------- REGISTER --------------------
@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = generate_password_hash(request.form["password"])

        user = User(username=username, email=email, password=password)
        db.session.add(user)
        db.session.commit()

        # After register → login (clean flow)
        return redirect(url_for("auth.login"))

    return render_template("register.html")


# -------------------- LOGIN --------------------
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = User.query.filter_by(email=request.form["email"]).first()

        if user and check_password_hash(user.password, request.form["password"]):
            login_user(user)

            # IMPORTANT: redirect to create group (not dashboard)
            return redirect(url_for("groups.create_group"))

    return render_template("login.html")


# -------------------- LOGOUT --------------------
@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))