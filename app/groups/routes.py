from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from app.models import Group, GroupMember
from app.extensions import db
from app.models import User, FriendRequest
import random
import string

groups_bp = Blueprint("groups", __name__, url_prefix="/groups")


def generate_invite_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))


@groups_bp.route("/dashboard")
@login_required
def dashboard():

    memberships = GroupMember.query.filter_by(user_id=current_user.id).all()
    group_ids = [m.group_id for m in memberships]
    groups = Group.query.filter(Group.id.in_(group_ids)).all()

    # friend requests received
    friend_requests = FriendRequest.query.filter_by(
        receiver_id=current_user.id,
        status="pending"
    ).all()

    # friends count
    friends_count = FriendRequest.query.filter(
        ((FriendRequest.sender_id == current_user.id) |
         (FriendRequest.receiver_id == current_user.id)) &
        (FriendRequest.status == "accepted")
    ).count()

    return render_template(
        "dashboard.html",
        groups=groups,
        user=current_user,
        friend_requests=friend_requests,
        friends_count=friends_count
    )
@groups_bp.route("/search_users", methods=["POST"])
@login_required
def search_users():

    username = request.form["username"]

    users = User.query.filter(
        User.username.contains(username),
        User.id != current_user.id
    ).all()

    return render_template(
        "search_results.html",
        users=users
    )
@groups_bp.route("/send_request/<int:user_id>")
@login_required
def send_request(user_id):

    existing = FriendRequest.query.filter_by(
        sender_id=current_user.id,
        receiver_id=user_id
    ).first()

    if existing:
        flash("Request already sent", "info")
        return redirect(url_for("groups.dashboard"))

    request_obj = FriendRequest(
        sender_id=current_user.id,
        receiver_id=user_id,
        status="pending"
    )

    db.session.add(request_obj)
    db.session.commit()

    flash("Friend request sent!", "success")

    return redirect(url_for("groups.dashboard"))


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

        # creator automatically becomes a member
        member = GroupMember(
            user_id=current_user.id,
            group_id=group.id
        )

        db.session.add(member)
        db.session.commit()

        flash(f"Group created! Invite Code: {invite_code}", "invite")

        return redirect(url_for("groups.dashboard"))

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

        # check if already a member
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

        return redirect(url_for("tasks.view_tasks", group_id=group.id))

    return render_template("join_group.html")