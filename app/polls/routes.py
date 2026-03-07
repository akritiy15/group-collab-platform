from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from sqlalchemy.exc import IntegrityError

from app.models import Poll, PollOption, Group, PollVote
from app.extensions import db

polls_bp = Blueprint("polls", __name__, url_prefix="/polls")


# ---------------- VIEW POLLS ----------------
@polls_bp.route("/<int:group_id>")
@login_required
def view_polls(group_id):
    group = Group.query.get_or_404(group_id)

    polls = Poll.query.filter_by(group_id=group.id).all()

    # polls the current user has already voted in
    user_votes = {
        vote.poll_id
        for vote in PollVote.query.filter_by(user_id=current_user.id).all()
    }

    return render_template(
        "polls.html",
        group=group,
        polls=polls,
        user_votes=user_votes
    )


# ---------------- CREATE POLL ----------------
@polls_bp.route("/create/<int:group_id>", methods=["GET", "POST"])
@login_required
def create_poll(group_id):
    group = Group.query.get_or_404(group_id)

    if request.method == "POST":
        question = request.form.get("question")
        options = request.form.getlist("options[]")

        # clean options
        options = [opt.strip() for opt in options if opt.strip()]

        if not question or len(options) < 2:
            flash("A poll needs a question and at least 2 options 🤔", "error")
            return redirect(url_for("polls.create_poll", group_id=group.id))

        poll = Poll(
            question=question,
            group_id=group.id
        )
        db.session.add(poll)
        db.session.commit()

        for opt in options:
            option = PollOption(
                text=opt,
                poll_id=poll.id,
                group_id=group.id
            )

            # safety: ensure votes exists
            if hasattr(option, "votes"):
                option.votes = 0

            db.session.add(option)

        db.session.commit()
        flash("Poll created successfully 🗳️", "success")

        return redirect(url_for("polls.view_polls", group_id=group.id))

    return render_template("create_poll.html", group=group)


# ---------------- VOTE ----------------
@polls_bp.route("/vote/<int:option_id>")
@login_required
def vote(option_id):
    option = PollOption.query.get_or_404(option_id)
    poll = option.poll

    vote = PollVote(
        poll_id=poll.id,
        user_id=current_user.id
    )

    try:
        db.session.add(vote)

        # safety check
        if hasattr(option, "votes"):
            option.votes += 1

        db.session.commit()

    except IntegrityError:
        db.session.rollback()
        flash("You already voted in this poll 👀", "error")

    return redirect(
        url_for("polls.view_polls", group_id=poll.group_id)
    )