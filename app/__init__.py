from flask import Flask
from .extensions import db, login_manager

def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "dev-secret"
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite3"

    db.init_app(app)
    login_manager.init_app(app)

    from .auth.routes import auth_bp
    app.register_blueprint(auth_bp)

    with app.app_context():
        from . import models
        db.create_all()

    return app