from discord.ext import commands
import sqlol.disql as sq #for some reason, we need to import it like we're doing so from the main function?
from clients.bot_vars import bot_vars
import copy
import json


class CustomBotClient(commands.Bot):


    async def on_ready(self):
        print(f'{self.user.name} has connected to Discord!')

        """
        just starts the bot and ensures that the database is there. 
        checking of the database is done in db_checker, in checks folder.
        """

        self.conn = bot_vars.conn #made this an attribute just in case.
        self.main_table = bot_vars.main_table #use these attributes in different cogs that require access to tables
        self.server_table = bot_vars.server_table

        print("\n ---------- Checking existence of database... ---------- \n")
        # USE THESE LISTS TO INITIALIZE USER/SERVER DATABASE; REMEMBER TO MODIFY THE DEFAULTS IF YOU'RE ADDING/REMOVING COLUMNS.
        #remember that data fetched from the table comes as a tuple in a list; in the tuple is the data's index + the columns, so to find the column we need, we must +1.
        server_cols = bot_vars.server_cols
        server_cols_type = bot_vars.server_cols
        sq.create_table(self.conn, self.server_table, server_cols, server_cols_type)

        user_cols = bot_vars.user_cols
        user_cols_type = bot_vars.user_cols_type
        sq.create_table(self.conn, self.main_table, user_cols, user_cols_type)        
        print('\n ---------- Database initialized. ---------- \n')
        

    
