import mysql.connector
from werkzeug.security import generate_password_hash
from config import DB

con = mysql.connector.connect(host=DB["host"], user=DB["user"], password=DB["password"])
cur = con.cursor()
for stmt in open("schema.sql", encoding="utf-8").read().split(";"):
    if stmt.strip():
        cur.execute(stmt)
cur.execute("INSERT INTO users (name,email,password_hash,role) VALUES (%s,%s,%s,'admin')",
            ("Admin", "admin@quizsphere.com", generate_password_hash("admin123")))
con.commit()
print("Database ready. Admin login: admin@quizsphere.com / admin123")
