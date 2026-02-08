from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required
from ..models import Poll, PollOption
from ..extensions import db

polls_bp = Blueprint("polls", __name__, url_prefix="/polls")

@polls_bp.route("/", methods=["GET", "POST"])
@login_required
def create_poll():
    if request.method == "POST":
        question = request.form["question"]
        options = request.form.getlist("options")

        poll = Poll(question=question)
        db.session.add(poll)
        db.session.commit()

        for opt in options:
            option = PollOption(text=opt, poll_id=poll.id)
            db.session.add(option)

        db.session.commit()
        return redirect(url_for("polls.polls"))

    all_polls = Poll.query.all()
    return render_template("polls/polls.html", polls=all_polls)


@polls_bp.route("/vote/<int:option_id>")
@login_required
def vote(option_id):
    option = PollOption.query.get(option_id)
    option.votes += 1
    db.session.commit()
    return redirect(url_for("polls.polls"))
