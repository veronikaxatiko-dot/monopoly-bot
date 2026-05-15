import sqlite3

conn = sqlite3.connect("monopoly.db")
cursor = conn.cursor()

# ИГРОКИ
cursor.execute("""
CREATE TABLE IF NOT EXISTS players (
    user_id INTEGER PRIMARY KEY,
    name TEXT,
    money INTEGER,
    position INTEGER,
    jail INTEGER,
    bankrupt INTEGER
)
""")

# УЧАСТКИ
cursor.execute("""
CREATE TABLE IF NOT EXISTS properties (
    position INTEGER PRIMARY KEY,
    owner_id INTEGER
)
""")

conn.commit()


# =========================
# PLAYER FUNCTIONS
# =========================

def add_player(user_id, name):
    cursor.execute("""
    INSERT OR IGNORE INTO players
    (user_id, name, money, position, jail, bankrupt)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (user_id, name, 1500, 0, 0, 0))

    conn.commit()


def get_player(user_id):
    cursor.execute("""
    SELECT * FROM players WHERE user_id=?
    """, (user_id,))

    return cursor.fetchone()


def update_player(user_id, money, position, jail, bankrupt):
    cursor.execute("""
    UPDATE players
    SET money=?, position=?, jail=?, bankrupt=?
    WHERE user_id=?
    """, (money, position, jail, bankrupt, user_id))

    conn.commit()


# =========================
# PROPERTY FUNCTIONS
# =========================

def buy_property(position, owner_id):
    cursor.execute("""
    INSERT OR REPLACE INTO properties
    (position, owner_id)
    VALUES (?, ?)
    """, (position, owner_id))

    conn.commit()


def get_property_owner(position):
    cursor.execute("""
    SELECT owner_id FROM properties
    WHERE position=?
    """, (position,))

    result = cursor.fetchone()

    if result:
        return result[0]

    return None