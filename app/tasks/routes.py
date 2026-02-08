from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user
from app.models import Task, Group
from app.extensions import db

tasks_bp = Blueprint("tasks", __name__, url_prefix="/tasks")


@tasks_bp.route("/create/<int:group_id>", methods=["GET", "POST"])
@login_required
def create_task(group_id):
    group = Group.query.get_or_404(group_id)

    if request.method == "POST":
        title = request.form["title"]

        task = Task(
            title=title,
            status="Pending",
            group_id=group.id
        )
        db.session.add(task)
        db.session.commit()

        return redirect(url_for("groups.view_group", group_id=group.id))

    return render_template("tasks/create_task.html", group=group)


@tasks_bp.route("/status/<int:task_id>")
@login_required
def change_status(task_id):
    task = Task.query.get_or_404(task_id)
    task.status = "Completed" if task.status == "Pending" else "Pending"
    db.session.commit()

    return redirect(url_for("groups.view_group", group_id=task.group_id))
