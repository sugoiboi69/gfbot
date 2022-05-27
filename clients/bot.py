from discord.ext import commands
import sqlol.disql as sq #for some reason, we need to import it like we're doing so from the main function?
from clients.bot_vars import bot_vars
import copy
import json


class Bot(commands.Bot):
    async def on_ready(self):
        with open("config.json", "r") as f:
                self.bot_config = json.load(f)
        print(f'{self.user.name} has connected to Discord!')

        """
        starts the bot and ensures that the database is there. 
        checking of the database is done in db_checker, found in the checks folder.
        afterwards, loads config from json file; if there is none, loads the default and asks user to set it.
        """

        self.conn = bot_vars.conn #made this an attribute just in case.
        self.main_table = bot_vars.main_table #use these attributes in different cogs that require access to tables
        self.server_table = bot_vars.server_table

        print("\n ---------- Checking existence of database... ---------- \n")

        server_cols = bot_vars.server_cols
        server_cols_type = bot_vars.server_cols
        sq.create_table(self.conn, self.server_table, server_cols, server_cols_type)

        user_cols = bot_vars.user_cols
        user_cols_type = bot_vars.user_cols_type
        sq.create_table(self.conn, self.main_table, user_cols, user_cols_type)        

        print('\n ---------- Database initialized. ---------- \n')

        for guild in self.guilds:
            for member in guild.members:
                sq.update_value(self.conn, bot_vars.main_table, "uid", member.id, "active_game", '') #makes sure all users are not shown as in active_game.

        
        

    
