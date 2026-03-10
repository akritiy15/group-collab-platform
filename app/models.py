from .extensions import db
from flask_login import UserMixin
from datetime import datetime 

# USER MODEL (for login)
class User(db.Model, UserMixin):

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(80), unique=True, nullable=False)

    email = db.Column(db.String(120), unique=True, nullable=False)

    password = db.Column(db.String(200), nullable=False)

    bio = db.Column(db.String(300))

    profile_picture = db.Column(db.String(200), default="default.png")

    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    amount = db.Column(db.Float)
    paid_by = db.Column(db.Integer)
    group_id = db.Column(db.Integer)

    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


class ExpenseSplit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    expense_id = db.Column(db.Integer)
    user_id = db.Column(db.Integer)
    amount_owed = db.Column(db.Float)


# LOCATION MODEL
class UserLocation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    group_id = db.Column(db.Integer)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)

from datetime import datetime




# ---------- GROUPS ----------
class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    invite_code = db.Column(db.String(10), unique=True, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey("user.id"))
    tasks = db.relationship("Task", backref="group", lazy=True)
    polls = db.relationship("Poll", backref="group", lazy=True)


class GroupMember(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    group_id = db.Column(db.Integer, db.ForeignKey("group.id"))
    user = db.relationship("User", backref="group_memberships")

# ---------- TASK ----------
class TaskAssignee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    status = db.Column(db.String(50), default="pending")
    group_id = db.Column(db.Integer, db.ForeignKey("group.id"))

    # track creator and assignees
    created_by = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    # assigned_to removed, using many-to-many

    # relationships for convenience
    creator = db.relationship("User", foreign_keys=[created_by], backref="created_tasks")
    assignees = db.relationship('User', secondary='task_assignee', backref='assigned_tasks')


# ---------- POLLS ----------
class Poll(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(300))
    group_id = db.Column(db.Integer, db.ForeignKey("group.id"))
    created_by = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    options = db.relationship("PollOption", backref="poll", lazy=True)
    creator = db.relationship("User", foreign_keys=[created_by], backref="created_polls")

class PollOption(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(200), nullable=False)
    votes = db.Column(db.Integer, default=0)   # ✅ ADD THIS
    poll_id = db.Column(db.Integer, db.ForeignKey("poll.id"))
    group_id = db.Column(db.Integer, db.ForeignKey("group.id"))


class PollVote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    poll_id = db.Column(db.Integer, db.ForeignKey("poll.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    __table_args__ = (
        db.UniqueConstraint("poll_id", "user_id", name="unique_user_poll_vote"),
    )
class FriendRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    sender_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    status = db.Column(db.String(20), default="pending")  # pending / accepted / rejected


# ---------------- FRIENDSHIP ----------------
class Friendship(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    friend_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)