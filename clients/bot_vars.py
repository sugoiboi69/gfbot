import sqlol.disql as sq
import json


class bot_vars(): 

    """
    just decided to store all the bot's variables here so its easier see and reference in other cogs.
    most of it pertains to db configs and stuff
    """

    #db names, connection, default server config
    main_table = "disc"
    server_table = "server"
    conn = sq.create_connection(r"disc.db")
    config = {
        "bn_ping": 0,
        "bn_ping_channel": 0,
    }

    #server db config
    server_cols = ["server", "server_id", "config"]
    server_cols_type = ["text", "text", "text"]
    server_default_config = json.dumps(config)
    server_default = ["", "", server_default_config]

    #user db config
    user_cols = ["user", "uid", "money"]
    user_cols_type = ["text", "text", "integer"]
    user_default = ['', '', 0]
