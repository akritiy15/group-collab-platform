from app import create_app
from app.extensions import db
from flask_migrate import upgrade

# when flask_migrate.upgrade is called it needs current_app context
app = create_app()
with app.app_context():
    print("Running alembic upgrade...")
    upgrade()
    print("Upgrade complete")
