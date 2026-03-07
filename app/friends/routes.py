from flask import Blueprint, redirect, url_for, flash
from flask_login import login_required, current_user

from app.models import User, FriendRequest, Friendship
from app.extensions import db

friends_bp = Blueprint("friends", __name__)


# SEND FRIEND REQUEST
@friends_bp.route("/send-request/<int:user_id>")
@login_required
def send_request(user_id):

    existing = FriendRequest.query.filter_by(
        sender_id=current_user.id,
        receiver_id=user_id
    ).first()

    if existing:
        flash("Request already sent")
        return redirect(url_for("groups.dashboard"))

    request = FriendRequest(
        sender_id=current_user.id,
        receiver_id=user_id
    )

    db.session.add(request)
    db.session.commit()

    flash("Friend request sent")
    return redirect(url_for("groups.dashboard"))


# ACCEPT REQUEST
@friends_bp.route("/accept-request/<int:request_id>")
@login_required
def accept_request(request_id):

    req = FriendRequest.query.get_or_404(request_id)

    req.status = "accepted"

    friendship1 = Friendship(
        user_id=req.sender_id,
        friend_id=req.receiver_id
    )

    friendship2 = Friendship(
        user_id=req.receiver_id,
        friend_id=req.sender_id
    )

    db.session.add(friendship1)
    db.session.add(friendship2)
    db.session.commit()

    flash("Friend added")
    return redirect(url_for("groups.dashboard"))


# REJECT REQUEST
@friends_bp.route("/reject-request/<int:request_id>")
@login_required
def reject_request(request_id):

    req = FriendRequest.query.get_or_404(request_id)

    req.status = "rejected"
    db.session.commit()

    flash("Request rejected")
    return redirect(url_for("groups.dashboard"))