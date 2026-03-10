from sqlalchemy import text
from app import create_app
from app.extensions import db

app = create_app()
with app.app_context():
    # show tables before
    result = db.session.execute(text("SELECT name FROM sqlite_master WHERE type='table';")).fetchall()
    print("tables before:", result)
    db.session.execute(text("DROP TABLE IF EXISTS _alembic_tmp_task"))
    db.session.commit()
    result = db.session.execute(text("SELECT name FROM sqlite_master WHERE type='table';")).fetchall()
    print("tables after:", result)
