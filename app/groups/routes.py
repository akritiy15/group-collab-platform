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

    # Get members for each group
    group_members = {}
    for group in groups:
        members = GroupMember.query.filter_by(group_id=group.id).all()
        group_members[group.id] = [m.user for m in members]

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
        group_members=group_members,
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

@groups_bp.route("/detail/<int:group_id>")
@login_required
def group_detail(group_id):

    # Check if user is member of the group
    membership = GroupMember.query.filter_by(
        user_id=current_user.id,
        group_id=group_id
    ).first()

    if not membership:
        flash("You are not a member of this group", "error")
        return redirect(url_for("groups.dashboard"))

    group = Group.query.get_or_404(group_id)

    # Get all members
    member_objects = GroupMember.query.filter_by(group_id=group_id).all()
    members = [m.user for m in member_objects]

    # Check if current user is admin
    is_admin = current_user.id == group.created_by
    print(f"DEBUG: current_user.id = {current_user.id}, group.created_by = {group.created_by}, is_admin = {is_admin}")

    # Get friends who are not already in the group
    accepted_friends = FriendRequest.query.filter(
        ((FriendRequest.sender_id == current_user.id) |
         (FriendRequest.receiver_id == current_user.id)) &
        (FriendRequest.status == "accepted")
    ).all()

    friend_ids = set()
    for friend_req in accepted_friends:
        if friend_req.sender_id == current_user.id:
            friend_ids.add(friend_req.receiver_id)
        else:
            friend_ids.add(friend_req.sender_id)

    # Remove members who are already in the group
    member_ids = {m.user_id for m in member_objects}
    available_friend_ids = friend_ids - member_ids

    available_friends = User.query.filter(User.id.in_(available_friend_ids)).all() if available_friend_ids else []

    return render_template(
        "group_detail.html",
        group=group,
        members=members,
        is_admin=is_admin,
        available_friends=available_friends
    )


@groups_bp.route("/add_member/<int:group_id>", methods=["POST"])
@login_required
def add_member(group_id):

    # Check if user is admin
    group = Group.query.get_or_404(group_id)
    if current_user.id != group.created_by:
        flash("Only group admins can add members", "error")
        return redirect(url_for("groups.group_detail", group_id=group_id))

    user_id = request.form.get("user_id")
    if not user_id:
        flash("No user specified", "error")
        return redirect(url_for("groups.group_detail", group_id=group_id))

    # Check if user is already a member
    existing = GroupMember.query.filter_by(
        user_id=user_id,
        group_id=group_id
    ).first()

    if existing:
        flash("User is already a member of this group", "error")
        return redirect(url_for("groups.group_detail", group_id=group_id))

    # Add the member
    member = GroupMember(user_id=user_id, group_id=group_id)
    db.session.add(member)
    db.session.commit()

    user = User.query.get(user_id)
    flash(f"Added {user.username} to the group", "success")
    return redirect(url_for("groups.group_detail", group_id=group_id))


@groups_bp.route("/remove_member/<int:group_id>/<int:user_id>", methods=["POST"])
@login_required
def remove_member(group_id, user_id):

    group = Group.query.get_or_404(group_id)

    # Check permissions: admin can remove anyone, users can remove themselves
    if current_user.id != group.created_by and current_user.id != user_id:
        flash("You don't have permission to remove this member", "error")
        return redirect(url_for("groups.group_detail", group_id=group_id))

    # Can't remove the last admin
    if user_id == group.created_by:
        member_count = GroupMember.query.filter_by(group_id=group_id).count()
        if member_count <= 1:
            flash("Cannot remove the last member of the group", "error")
            return redirect(url_for("groups.group_detail", group_id=group_id))

    member = GroupMember.query.filter_by(
        user_id=user_id,
        group_id=group_id
    ).first()

    if not member:
        flash("User is not a member of this group", "error")
        return redirect(url_for("groups.group_detail", group_id=group_id))

    user = User.query.get(user_id)
    db.session.delete(member)
    db.session.commit()

    if user_id == current_user.id:
        flash("You have left the group", "success")
        return redirect(url_for("groups.dashboard"))
    else:
        flash(f"Removed {user.username} from the group", "success")
        return redirect(url_for("groups.group_detail", group_id=group_id))


@groups_bp.route("/update_group_picture/<int:group_id>", methods=["POST"])
@login_required
def update_group_picture(group_id):

    # Check if user is admin
    group = Group.query.get_or_404(group_id)
    if current_user.id != group.created_by:
        flash("Only group admins can update the group picture", "error")
        return redirect(url_for("groups.group_detail", group_id=group_id))

    if 'profile_picture' not in request.files:
        flash("No file selected", "error")
        return redirect(url_for("groups.group_detail", group_id=group_id))

    file = request.files['profile_picture']
    if file.filename == '':
        flash("No file selected", "error")
        return redirect(url_for("groups.group_detail", group_id=group_id))

    if file:
        # Save the file
        import os
        from werkzeug.utils import secure_filename

        filename = secure_filename(f"group_{group_id}_{file.filename}")
        file_path = os.path.join('app/static/group_pics', filename)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        file.save(file_path)

        # Update the group
        group.profile_picture = filename
        db.session.commit()

        flash("Group picture updated successfully", "success")

    return redirect(url_for("groups.group_detail", group_id=group_id))