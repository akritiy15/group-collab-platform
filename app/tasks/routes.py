from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from flask_login import login_required, current_user
from app.models import Task, Group, TaskAssignee, GroupMember
from app.extensions import db
from sqlalchemy.orm import joinedload

tasks_bp = Blueprint("tasks", __name__, url_prefix="/tasks")


@tasks_bp.route("/<int:group_id>", methods=["GET", "POST"])
@login_required
def view_tasks(group_id):
    group = Group.query.get_or_404(group_id)

    # Get filter from query params
    filter_status = request.args.get('filter', 'all')

    if request.method == "POST":
        title = request.form["title"]
        task = Task(title=title, status="Pending", group_id=group.id, created_by=current_user.id)
        db.session.add(task)
        db.session.flush()  # to get task.id

        # assign to selected members
        assignee_ids = request.form.getlist('assignees')
        for user_id in assignee_ids:
            assignee = TaskAssignee(task_id=task.id, user_id=int(user_id))
            db.session.add(assignee)

        db.session.commit()
        return redirect(url_for("tasks.view_tasks", group_id=group.id, filter=filter_status))

    # Filter tasks based on status
    query = Task.query.filter_by(group_id=group.id).options(joinedload(Task.creator), joinedload(Task.assignees))
    if filter_status == 'pending':
        query = query.filter_by(status="Pending")
    elif filter_status == 'completed':
        query = query.filter_by(status="Completed")
    tasks = query.all()

    group_members = GroupMember.query.filter_by(group_id=group_id).all()
    return render_template("tasks.html", group=group, tasks=tasks, group_members=group_members, filter_status=filter_status)


@tasks_bp.route("/toggle/<int:task_id>", methods=["POST"])
@login_required
def toggle_task(task_id):
    task = Task.query.get_or_404(task_id)
    filter_status = request.form.get('filter', 'all')
    task.status = "Completed" if task.status == "Pending" else "Pending"
    db.session.commit()
    
    if 'filter' in request.form:  # AJAX request
        return jsonify({'success': True, 'new_status': task.status})
    
    return redirect(url_for("tasks.view_tasks", group_id=task.group_id, filter=filter_status))


@tasks_bp.route("/remove_completed/<int:group_id>", methods=["POST"])
@login_required
def remove_completed_tasks(group_id):
    group = Group.query.get_or_404(group_id)
    filter_status = request.form.get('filter', 'all')
    # Ensure user is member of the group
    member = GroupMember.query.filter_by(user_id=current_user.id, group_id=group_id).first()
    if not member:
        if 'filter' in request.form:
            return jsonify({'success': False, 'error': 'Permission denied'})
        return redirect(url_for("groups.view_groups"))  # or some error

    # Delete completed tasks
    completed_tasks = Task.query.filter_by(group_id=group_id, status="Completed").all()
    for task in completed_tasks:
        # Also delete assignees
        TaskAssignee.query.filter_by(task_id=task.id).delete()
        db.session.delete(task)
    db.session.commit()
    
    if 'filter' in request.form:
        return jsonify({'success': True, 'deleted_count': len(completed_tasks)})
    
    return redirect(url_for("tasks.view_tasks", group_id=group_id, filter=filter_status))


@tasks_bp.route("/delete_task/<int:task_id>", methods=["POST"])
@login_required
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    group_id = task.group_id
    filter_status = request.form.get('filter', 'all')
    # Ensure user is member of the group
    member = GroupMember.query.filter_by(user_id=current_user.id, group_id=group_id).first()
    if not member:
        if 'filter' in request.form:
            return jsonify({'success': False, 'error': 'Permission denied'})
        return redirect(url_for("groups.view_groups"))

    # Delete assignees first
    TaskAssignee.query.filter_by(task_id=task.id).delete()
    db.session.delete(task)
    db.session.commit()
    
    if 'filter' in request.form:
        return jsonify({'success': True})
    
    return redirect(url_for("tasks.view_tasks", group_id=group_id, filter=filter_status))