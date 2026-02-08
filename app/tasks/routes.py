from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required
from ..models import Task, User
from ..extensions import db

tasks_bp = Blueprint("tasks", __name__, url_prefix="/tasks")

@tasks_bp.route("/", methods=["GET", "POST"])
@login_required
def tasks():
    users = User.query.all()

    if request.method == "POST":
        title = request.form["title"]
        user_id = request.form["assigned_to"]

        task = Task(title=title, assigned_to_id=user_id)
        db.session.add(task)
        db.session.commit()

        return redirect(url_for("tasks.tasks"))

    all_tasks = Task.query.all()
    return render_template("tasks/tasks.html", tasks=all_tasks, users=users)


@tasks_bp.route("/status/<int:task_id>")
@login_required
def change_status(task_id):
    task = Task.query.get(task_id)
    task.status = "completed" if task.status == "pending" else "pending"
    db.session.commit()
    return redirect(url_for("tasks.tasks"))
