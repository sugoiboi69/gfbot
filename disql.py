import sqlite3
import pandas as pd
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

#table currently consists of: user, user_id, money, osu_name
#table name is currently: disc
#table path is path = "disc.db"; probably better to try put it online somewhere so its always accessible

def create_table(conn, tablename):
    c = conn.cursor()
    try:
        c.execute("""CREATE TABLE disc (
            user text,
            uid text,
            money integer,
            osu_name text  
        )
        """)
        conn.commit()

    except:
        print("the table already exists.")


def pandas(conn, tablename): #returns pandas of the table if you want LOL
    c = conn.cursor()
    x = "SELECT * FROM " + tablename
    df = pd.read_sql_query(x, conn)
    return df


def get_tables(conn):
    c = conn.cursor()
    x = """SELECT name FROM sqlite_master  
  WHERE type='table';"""
    c.execute(x)
    print(c.fetchall())


def search_id(conn, table, uid):
    c = conn.cursor()
    x = "SELECT rowid, * from " + table + " WHERE uid = '" + str(uid) + "'"
    c.execute(x)
    return c.fetchall()


def add_column(conn, table, colname, type):
    c = conn.cursor()
    c.execute(f"ALTER TABLE {table} ADD COLUMN {colname} {type};")
    conn.commit()


def add_to_table(conn, table, userinfo):
    c = conn.cursor()
    x = "INSERT INTO "+ table +" VALUES (?,?,?,?)" #note that this has to change with more columns!!!
    c.execute(x, userinfo)
    conn.commit()


def update_value(conn, table, uid, updated_column, val):
    #try:
        c = conn.cursor()
        c.execute(f"""UPDATE {table} SET {updated_column} = '{val}'
            WHERE uid = '{uid}'
        """)
        conn.commit()
    #except:
        #print("there was some error; check your column name, datatype, etc.")
        

def close(conn):
    conn.close()
    print('sql connection closed')


### testing ###
tablename = "disc"
conn = create_connection(r"C:\Users\Hisham\Documents\GitHub\gfbot\disc.db")
create_table(conn, tablename)
#add_column(conn, tablename, "osu_name", "text")
d = pandas(conn, tablename)
print(d)
### testing ###




