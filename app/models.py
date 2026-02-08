from .extensions import db
from flask_login import UserMixin

# USER MODEL (for login)
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(200))


# EXPENSE MODEL
class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    amount = db.Column(db.Float)
    paid_by = db.Column(db.String(100))
    group_id = db.Column(db.Integer)


# EXPENSE SPLIT
class ExpenseSplit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    expense_id = db.Column(db.Integer)
    user_id = db.Column(db.String(100))
    share_amount = db.Column(db.Float)


# LOCATION MODEL
class UserLocation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    group_id = db.Column(db.Integer)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)

from datetime import datetime

# ---------- USER ----------
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

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

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    # assigned_to = db.Column(db.Integer, db.ForeignKey("user.id"))
    status = db.Column(db.String(50), default="pending")
    group_id = db.Column(db.Integer, db.ForeignKey("group.id"))


class Poll(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(300))
    group_id = db.Column(db.Integer, db.ForeignKey("group.id"))


class PollOption(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(200))
    poll_id = db.Column(db.Integer, db.ForeignKey("poll.id"))
    group_id = db.Column(db.Integer, db.ForeignKey("group.id"))
