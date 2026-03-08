from flask import Blueprint, render_template, request, redirect, url_for
from app.extensions import db
from app.models import Expense, ExpenseSplit, Group, GroupMember, User

expenses_bp = Blueprint('expenses', __name__)


@expenses_bp.route("/expenses/<int:group_id>", methods=["GET", "POST"])
def expenses_home(group_id):

    # ---------------------------
    # POST REQUEST (ADD EXPENSE)
    # ---------------------------
    if request.method == "POST":

        title = request.form["title"]
        amount = float(request.form["amount"])
        paid_by = int(request.form["paid_by"])

        participants = request.form.getlist("participants")

        if not participants:
            return redirect(url_for("expenses.expenses_home", group_id=group_id))

        new_expense = Expense(
            title=title,
            amount=amount,
            paid_by=paid_by,
            group_id=group_id
        )

        db.session.add(new_expense)
        db.session.commit()

        split_amount = amount / len(participants)

        for user_id in participants:

            split = ExpenseSplit(
                expense_id=new_expense.id,
                user_id=int(user_id),
                amount_owed=split_amount
            )

            db.session.add(split)

        db.session.commit()

        return redirect(url_for("expenses.expenses_home", group_id=group_id))


    # ---------------------------
    # GET REQUEST (LOAD PAGE)
    # ---------------------------

    expenses = Expense.query.filter_by(group_id=group_id).all()

    splits = db.session.query(ExpenseSplit) \
        .join(Expense, ExpenseSplit.expense_id == Expense.id) \
        .filter(Expense.group_id == group_id) \
        .all()

    members = GroupMember.query.filter_by(group_id=group_id).all()


    # ---------------------------
    # BALANCE CALCULATION
    # ---------------------------

    balances = {}

    for s in splits:
        balances.setdefault(s.user_id, 0)
        balances[s.user_id] -= s.amount_owed

    for e in expenses:
        balances.setdefault(e.paid_by, 0)
        balances[e.paid_by] += e.amount


    # ---------------------------
    # CALCULATE TOTALS
    # ---------------------------

    owed_by_you = 0
    owed_to_you = 0

    for user_id, amount in balances.items():

        if amount < 0:
            owed_by_you += abs(amount)

        if amount > 0:
            owed_to_you += amount


    # ---------------------------
    # USER MAP (id -> username)
    # ---------------------------

    users = User.query.all()
    user_map = {u.id: u.username for u in users}


    return render_template(
        "expenses.html",
        expenses=expenses,
        balances=balances,
        owed_by_you=owed_by_you,
        owed_to_you=owed_to_you,
        members=members,
        user_map=user_map,
        group=Group.query.get(group_id)
    )