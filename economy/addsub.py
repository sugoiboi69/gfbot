from clients.bot_vars import bot_vars
import sqlol.disql as sq


#the basic 2 functions that add or subtract money and write it to the database.

def add(uid, amount):
    cur = sq.search_id(bot_vars.conn, bot_vars.main_table, 'uid', uid)[0][3]
    now = cur + amount
    sq.update_value(bot_vars.conn, bot_vars.main_table, "uid", uid, "money", now)
    return 1

def sub(uid, amount):
    cur = sq.search_id(bot_vars.conn, bot_vars.main_table, 'uid', uid)[0][3]
    if cur < amount:
        print(f"Tried to subtract ${amount} from user {uid} but only had {cur}.")
        return 0
    else:
        now = cur-amount
        sq.update_value(bot_vars.conn, bot_vars.main_table, "uid", uid, "money", now)
        return 1

def bal(uid):
    return sq.search_id(bot_vars.conn, bot_vars.main_table, 'uid', uid)[0][3]
