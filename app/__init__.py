from flask import Flask
from .extensions import db, login_manager
from .models import User
from .tasks.routes import tasks_bp
from .polls.routes import polls_bp

def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "dev-secret"
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite3"

    db.init_app(app)
    login_manager.init_app(app)
    
    from .location.routes import location_bp
    app.register_blueprint(location_bp)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    

    # register auth blueprint
    from .auth.routes import auth_bp
    app.register_blueprint(auth_bp)
    from .groups.routes import groups_bp
    app.register_blueprint(groups_bp)
    from .tasks.routes import tasks_bp
    app.register_blueprint(tasks_bp)
    from .polls.routes import polls_bp
    app.register_blueprint(polls_bp)

    # register expenses blueprint  ← MOVED HERE
    from .expenses.routes import expenses_bp
    app.register_blueprint(expenses_bp)

    with app.app_context():
        db.create_all()

    return app


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

