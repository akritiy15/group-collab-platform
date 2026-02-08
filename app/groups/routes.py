from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import login_required, current_user
from app.models import Group, GroupMember
from app.extensions import db
import random, string

groups_bp = Blueprint("groups", __name__, url_prefix="/groups")

def generate_invite_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))


@groups_bp.route("/create", methods=["GET", "POST"])
@login_required
def create_group():
    if request.method == "POST":
        name = request.form["name"]
        code = generate_invite_code()

        group = Group(
            name=name,
            invite_code=code,
            created_by=current_user.id
        )
        db.session.add(group)
        db.session.commit()

        db.session.add(GroupMember(
            user_id=current_user.id,
            group_id=group.id
        ))
        db.session.commit()

        return redirect(url_for("auth.dashboard"))

    return render_template("create_group.html")


@groups_bp.route("/join", methods=["GET", "POST"])
@login_required
def join_group():
    if request.method == "POST":
        code = request.form["invite_code"]
        group = Group.query.filter_by(invite_code=code).first()

        if group:
            exists = GroupMember.query.filter_by(
                user_id=current_user.id,
                group_id=group.id
            ).first()

            if not exists:
                db.session.add(GroupMember(
                    user_id=current_user.id,
                    group_id=group.id
                ))
                db.session.commit()

        return redirect(url_for("auth.dashboard"))

    return render_template("join_group.html")