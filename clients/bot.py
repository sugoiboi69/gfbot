from discord.ext import commands
import sqlol.disql as sq #for some reason, we need to import it like we're doing so from the main function?
from clients.bot_vars import bot_vars
import copy
import json


class Bot(commands.Bot):
    async def on_ready(self):
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

        try:
            with open("config.json", "r") as f:
                self.bot_config = json.load(f)
            print("Current bot configuration settings: ")
            for key in self.bot_config.keys():
                print(str(key) + ": " + str(self.bot_config[key]))
        except:
            print("Seems there was no config found. Creating one...")
            
            Bot.set_config(self)
            with open("config.json", "r") as f:
                self.bot_config = json.load(f)
                
        print('\n ---------- Bot configuration loaded. ---------- \n')
        

    def set_config(self): #this function creates bot config file based on user preference.
        print("We will be setting each config setting's value.")
        new_config = copy.copy(bot_vars.bot_config)
        for key in new_config.keys():
            t = type(new_config[key]).__name__
            if t == "int" or t == "str":
                setting = input(f"Please input your intended value for the setting '{str(key)}'. The type must be {t}: ")
                if t == "str" and type(setting).__name__ == t:
                    new_config[key] = setting
                else:
                    while not setting.isdigit():
                        setting = input("It has to be an integer: ")
                    new_config[key] = int(setting)
            elif t == "list":
                setting = input(f"Please input your intended values for the list setting '{str(key)}'. To stop, enter STOP: ")
                while setting != "STOP":
                    new_config[key].append(setting)
                    setting = input(f"Enter the next entry: ")

        print("Finished setting configuration for the bot. Here are your settings: ")
        for key in new_config.keys():
            print(str(key) + ": " + str(new_config[key]))
        self.bot_config = new_config
        with open("config.json", "w") as f:
            json.dump(new_config, f, indent=2)

        

    
