import sqlite3
conn = sqlite3.connect('data.db')
conn.execute("CREATE TABLE accounts(id INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT,mob TEXT,mail TEXT,psw TEXT)")
conn.execute("CREATE TABLE s_road(id INTEGER PRIMARY KEY AUTOINCREMENT,s_name TEXT,accuracy TEXT,user TEXT)")

cur = conn.execute("SELECT * FROM accounts")
print(cur.fetchall())
