import sqlite3
from sqlite3 import Error

def create_connection(path):
    connection = None
    try:
        connection = sqlite3.connect(path)
        print("Connection to SQLite DB successful")
    except Error as e:
        print(f"The error '{e}' occurred")
    return connection

#conn = create_connection(path)
#c = conn.cursor()

#table currently consists of: user, user_id, money
#table name is currently: disc
#table path is path = "D:\\Documents\gfbot_sql\disc.db" 

def add_to_table(conn, table, userinfo):
    c = conn.cursor()
    c.execute("INSERT INTO {table} VALUES (?,?,?)", userinfo)
    conn.commit()

def update_money(conn, table, uid, money):
    c = conn.cursor()
    c.execute("""UPDATE {table} SET money = {money}
        WHERE user_id = {uid}
    """)
    conn.commit()

def close(conn):
    conn.close()
    print('sql connection closed')





