import sqlite3

conn = sqlite3.connect('instance/db.sqlite3')
c = conn.cursor()
c.execute("PRAGMA table_info(task);")
print(c.fetchall())
