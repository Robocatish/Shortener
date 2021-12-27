import sqlite3

def checkBase():
    try:
        con = sqlite3.connect('database.db')
        cursor = con.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS "users"(
            "id" INTEGER,
            "login" TEXT,
            "password" TEXT,
            PRIMARY KEY("id" AUTOINCREMENT));""")
        cursor.execute("""CREATE TABLE IF NOT EXISTS "links"(
            "id" INTEGER,
            "user_id" INTEGER,
            "name" TEXT,
            "link" TEXT,
            "status" TEXT NOT NULL,
            PRIMARY KEY("id" AUTOINCREMENT),
            FOREIGN KEY("user_id") REFERENCES "users"("id"));""")
        con.commit()
    except sqlite3.error:
        print ("not create")
    finally:
        con.close()

def getUser(user_id):    
    con = sqlite3.connect('database.db')
    cursor = con.cursor()
    res = cursor.execute("""SELECT * FROM users WHERE id = ? LIMIT 1""",(user_id)).fetchone()
    if not res:
        return False   
    return res