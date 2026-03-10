import sqlite3
conn = sqlite3.connect('instance/db.sqlite3')
c = conn.cursor()
c.execute("PRAGMA table_info(task);")
print("task columns:", c.fetchall())
c.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='task';")
print("task create sql:", c.fetchone())