import sqlite3

conn = sqlite3.connect('instance/db.sqlite3')
c = conn.cursor()
c.execute("SELECT name FROM sqlite_master WHERE type='table';")
print('tables', c.fetchall())
c.execute("SELECT * FROM alembic_version;")
print('alembic_version rows', c.fetchall())
