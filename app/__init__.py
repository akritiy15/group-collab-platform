from flask import Flask
from .extensions import db, login_manager

def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "dev-secret"
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite3"

    db.init_app(app)
    login_manager.init_app(app)

    # ---- Register blueprints ----
    from .auth.routes import auth_bp
    from .groups.routes import groups_bp
    from .tasks.routes import tasks_bp
    from .polls.routes import polls_bp
    from .expenses.routes import expenses_bp
    from .location.routes import location_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(groups_bp)
    app.register_blueprint(tasks_bp)
    app.register_blueprint(polls_bp)
    app.register_blueprint(expenses_bp)
    app.register_blueprint(location_bp)

    # ---- Create tables ----
    with app.app_context():
        from . import models   # models imported ONLY here
        db.create_all()

    return app


# ---- Flask-Login user loader (ONLY ONE, ONLY HERE) ----
from .models import User

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))