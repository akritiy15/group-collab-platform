from flask import Blueprint, render_template, request
from app.extensions import db
from app.models import Expense, ExpenseSplit

expenses_bp = Blueprint('expenses', __name__)

@expenses_bp.route("/expenses", methods=["GET", "POST"])
def expenses_home():

    if request.method == "POST":
        title = request.form["title"]
        amount = float(request.form["amount"])
        paid_by = request.form["paid_by"]
        members = request.form["members"].split(",")

        new_expense = Expense(
            title=title,
            amount=amount,
            paid_by=paid_by,
            group_id=1
        )

        db.session.add(new_expense)
        db.session.commit()

        # split logic
        split_amount = amount / len(members)

        for user in members:
         split = ExpenseSplit(
         expense_id=new_expense.id,
         user_id=user.strip(),
         share_amount=split_amount
            )
        db.session.add(split)

        db.session.commit()

    expenses = Expense.query.all()
    splits = ExpenseSplit.query.all()

    # calculate balances
    balances = {}

    for s in splits:
        balances.setdefault(s.user_id, 0)
        balances[s.user_id] -= s.share_amount

    for e in expenses:
        balances.setdefault(e.paid_by, 0)
        balances[e.paid_by] += e.amount

    return render_template("expenses.html", expenses=expenses, balances=balances)



