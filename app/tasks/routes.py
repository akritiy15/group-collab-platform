from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required
from app.models import Task, Group
from app.extensions import db

tasks_bp = Blueprint("tasks", __name__, url_prefix="/tasks")


@tasks_bp.route("/<int:group_id>", methods=["GET", "POST"])
@login_required
def view_tasks(group_id):
    group = Group.query.get_or_404(group_id)

    if request.method == "POST":
        title = request.form["title"]
        task = Task(title=title, status="Pending", group_id=group.id)
        db.session.add(task)
        db.session.commit()
        return redirect(url_for("tasks.view_tasks", group_id=group.id))

    tasks = Task.query.filter_by(group_id=group.id).all()
    return render_template("tasks.html", group=group, tasks=tasks)


@tasks_bp.route("/toggle/<int:task_id>")
@login_required
def toggle_task(task_id):
    task = Task.query.get_or_404(task_id)
    task.status = "Completed" if task.status == "Pending" else "Pending"
    db.session.commit()
    return redirect(url_for("tasks.view_tasks", group_id=task.group_id))