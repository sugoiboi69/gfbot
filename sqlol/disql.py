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


### table modifying/accessing functions


def create_table(conn, tablename: str, cols: list, type: list):
    c = conn.cursor()
    i=0
    string = ''
    while i < len(cols):
        string = string + cols[i] + ' ' + type[i] + ', '
        i+=1
    string = string[:-2]
    try:
        c.execute(f"""CREATE TABLE {tablename} (
            {string}
        )
        """)
        conn.commit()
        print(f"Table '{tablename}' created with columns: {string}.")

    except Exception as e:
        print(f"Creating the table '{tablename}' but ran into an error: " + str(e))


def get_all(conn):
    c = conn.cursor()
    return c.fetchall()


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

def get_columns(conn, table):
    c = conn.cursor()
    data = c.execute(f'''SELECT * FROM {table}''')
    for column in data.description:
        print(column[0])



def search_id(conn, table, col, val): #search for value "val" in column "col" in table "table"
    c = conn.cursor()
    c.execute(f"SELECT rowid, * from {table} WHERE {col} = '{val}'")
    return c.fetchall()


def add_column(conn, table, colname, type):
    c = conn.cursor()
    c.execute(f"ALTER TABLE {table} ADD COLUMN {colname} {type};")
    conn.commit()


def add_to_table(conn, table, info):
    c = conn.cursor()
    br = "("
    i=0
    while i < len(info):
        br = br + "?, "
        i+=1
    br = br[:-2]
    br = br + ")"

    c.execute(f"INSERT INTO {table} VALUES {br}", info)
    conn.commit()


def update_value(conn, table, identifier, id, updated_column, val):
    try:
        c = conn.cursor()
        c.execute(f"""UPDATE {table} SET {updated_column} = '{val}'
            WHERE {identifier} = '{id}'
        """)
        conn.commit()
    except Exception as e:
        print(f"Ran into an error while updating '{table}': " +str(e))
        

def close(conn):
    conn.close()
    print('sql connection closed')








