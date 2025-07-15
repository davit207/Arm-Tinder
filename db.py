import sqlite3

def init_db():
    conn = sqlite3.connect("bot.db")
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        name TEXT,
        age INTEGER,
        gender TEXT,
        city TEXT,
        photo_id TEXT,
        likes INTEGER DEFAULT 0,
        step TEXT
    )""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS likes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        from_id INTEGER,
        to_id INTEGER
    )""")
    conn.commit()
    conn.close()

def get_user(user_id):
    conn = sqlite3.connect("bot.db")
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    user = cur.fetchone()
    conn.close()
    return user

def add_user(user_id, username):
    conn = sqlite3.connect("bot.db")
    cur = conn.cursor()
    cur.execute("INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)", (user_id, username))
    conn.commit()
    conn.close()

def update_user_field(user_id, field, value):
    conn = sqlite3.connect("bot.db")
    cur = conn.cursor()
    cur.execute(f"UPDATE users SET {field}=? WHERE user_id=?", (value, user_id))
    conn.commit()
    conn.close()

def get_candidates(user_id):
    conn = sqlite3.connect("bot.db")
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE user_id!=? AND photo_id IS NOT NULL", (user_id,))
    candidates = cur.fetchall()
    conn.close()
    return candidates

def add_like(from_id, to_id):
    conn = sqlite3.connect("bot.db")
    cur = conn.cursor()
    cur.execute("INSERT INTO likes (from_id, to_id) VALUES (?, ?)", (from_id, to_id))
    cur.execute("UPDATE users SET likes = likes + 1 WHERE user_id=?", (to_id,))
    conn.commit()
    conn.close()

def check_match(user1, user2):
    conn = sqlite3.connect("bot.db")
    cur = conn.cursor()
    cur.execute("SELECT * FROM likes WHERE from_id=? AND to_id=?", (user2, user1))
    match = cur.fetchone()
    conn.close()
    return bool(match)

def get_likes(user_id):
    conn = sqlite3.connect("bot.db")
    cur = conn.cursor()
    cur.execute("SELECT username FROM users WHERE user_id IN (SELECT from_id FROM likes WHERE to_id=?)", (user_id,))
    likes = [i[0] for i in cur.fetchall()]
    conn.close()
    return likes

def get_matches(user_id):
    conn = sqlite3.connect("bot.db")
    cur = conn.cursor()
    cur.execute("""SELECT username FROM users WHERE user_id IN 
                   (SELECT from_id FROM likes WHERE to_id=?) 
                   AND user_id IN (SELECT to_id FROM likes WHERE from_id=?)""", (user_id, user_id))
    matches = [i[0] for i in cur.fetchall()]
    conn.close()
    return matches

def get_top_users():
    conn = sqlite3.connect("bot.db")
    cur = conn.cursor()
    cur.execute("SELECT username, likes FROM users ORDER BY likes DESC LIMIT 10")
    top = cur.fetchall()
    conn.close()
    return top
