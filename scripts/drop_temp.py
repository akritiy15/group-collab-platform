from app import create_app
from app.extensions import db
from sqlalchemy import text

app = create_app()
with app.app_context():
    print("Existing tables:", db.session.execute(text("SELECT name FROM sqlite_master WHERE type='table';")).fetchall())
    db.session.execute(text("DROP TABLE IF EXISTS _alembic_tmp_task"))
    db.session.commit()
    print("Dropped temp; now tables:", db.session.execute(text("SELECT name FROM sqlite_master WHERE type='table';")).fetchall())
