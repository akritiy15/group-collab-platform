from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os

from app.extensions import db
from app.models import Group, GroupMember, FriendRequest

profile_bp = Blueprint("profile", __name__, url_prefix="/profile")


# ---------------- PROFILE PAGE ----------------
@profile_bp.route("/")
@login_required
def view_profile():

    # groups the user belongs to
    memberships = GroupMember.query.filter_by(user_id=current_user.id).all()
    group_ids = [m.group_id for m in memberships]

    groups = Group.query.filter(Group.id.in_(group_ids)).all()

    # pending friend requests
    pending_requests = FriendRequest.query.filter_by(
        receiver_id=current_user.id,
        status="pending"
    ).all()

    return render_template(
        "profile.html",
        user=current_user,
        groups=groups,
        pending_requests=pending_requests
    )


# ---------------- EDIT PROFILE ----------------
@profile_bp.route("/edit", methods=["GET", "POST"])
@login_required
def edit_profile():

    if request.method == "POST":

        username = request.form["username"]
        bio = request.form["bio"]

        current_user.username = username
        current_user.bio = bio

        # profile picture upload
        file = request.files.get("profile_picture")

        if file and file.filename != "":
            filename = secure_filename(file.filename)

            path = os.path.join(
                "app/static/profile_pics",
                filename
            )

            file.save(path)

            current_user.profile_picture = filename

        db.session.commit()

        return redirect(url_for("profile.view_profile"))

    return render_template("edit_profile.html", user=current_user)