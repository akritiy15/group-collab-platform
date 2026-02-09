from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from app.models import Group, GroupMember
from app.extensions import db
import random
import string

groups_bp = Blueprint("groups", __name__, url_prefix="/groups")


def generate_invite_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))


# ---------------- CREATE GROUP ----------------
@groups_bp.route("/create", methods=["GET", "POST"])
@login_required
def create_group():
    if request.method == "POST":
        name = request.form["name"]

        invite_code = generate_invite_code()

        group = Group(
            name=name,
            invite_code=invite_code,
            created_by=current_user.id
        )
        db.session.add(group)
        db.session.commit()

        # creator becomes member
        member = GroupMember(
            user_id=current_user.id,
            group_id=group.id
        )
        db.session.add(member)
        db.session.commit()

        # ✅ flash success + invite code
        flash(f"Group created! Invite Code: {invite_code}", "invite")

        # stay on same page to show modal / message
        return redirect(url_for("groups.create_group"))

    return render_template("create_group.html")


# ---------------- JOIN GROUP ----------------
@groups_bp.route("/join", methods=["GET", "POST"])
@login_required
def join_group():
    if request.method == "POST":
        invite_code = request.form["invite_code"].upper()

        group = Group.query.filter_by(invite_code=invite_code).first()

        if not group:
            flash("Invalid invite code 😕", "error")
            return redirect(url_for("groups.join_group"))

        # avoid duplicate membership
        existing = GroupMember.query.filter_by(
            user_id=current_user.id,
            group_id=group.id
        ).first()

        if not existing:
            member = GroupMember(
                user_id=current_user.id,
                group_id=group.id
            )
            db.session.add(member)
            db.session.commit()

        # ✅ REDIRECT TO TASKS PAGE (THIS IS THE FIX)
        return redirect(url_for("tasks.view_tasks", group_id=group.id))

    return render_template("join_group.html")