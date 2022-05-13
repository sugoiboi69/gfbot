from discord.ext import commands
import sqlol.disql as sq #for some reason, we need to import it like we're doing so from the main function?
from clients.bot_vars import bot_vars
import copy
import json


class CustomBotClient(commands.Bot):

    @staticmethod
    async def std_dicts(refdict: dict, dict: dict): #ensures that keys in 'dict' are same as those in 'refdict'; adds or deletes entries otherwise.
        change = 0
        try:
            for key in refdict.keys():
                if key not in dict.keys():
                    change = 1
                    dict[key] = refdict[key]
            
            for key in dict.keys():
                if key not in refdict.keys():
                    change = 1
                    del dict[key]
            if change: return dict
            else: return change
        except Exception as e:
            print(f"Ran into an error: {str(e)}")


    async def on_ready(self):
        print(f'{self.user.name} has connected to Discord!')

        """
        upon initializing, create a database 'disc.db' with 2 tables, disc and server.
        disc holds user info, server holds server info + configuration info.
        we can change the columns for each table by modifying user_cols and server_cols; don't forget to add the types in the respective list.
        server config is a json with all required settings; the default is server_default_config.

        TO DO: move database online and create a cache system.
        """

        self.conn = bot_vars.conn #made this an attribute just in case.
        self.main_table = bot_vars.main_table #use these attributes in different cogs that require access to tables
        self.server_table = bot_vars.server_table

        print("\n ---------- Attempting to create databases. ---------- \n")
        # USE THESE LISTS TO INITIALIZE USER/SERVER DATABASE; REMEMBER TO MODIFY THE DEFAULTS IF YOU'RE ADDING/REMOVING COLUMNS.
        #remember that data fetched from the table comes as a tuple in a list; in the tuple is the data's index + the columns, so to find the column we need, we must +1.
        server_cols = bot_vars.server_cols
        server_cols_type = bot_vars.server_cols
        server_default_config = bot_vars.server_default_config
        server_default = bot_vars.server_default
        sq.create_table(self.conn, self.server_table, server_cols, server_cols_type)

        user_cols = ["user", "uid", "money"]
        user_cols_type = ["text", "text", "integer"]
        user_default = ['', '', 0]
        sq.create_table(self.conn, self.main_table, user_cols, user_cols_type)
        print("\n ---------- Initializing database... ---------- \n")

        for guild in self.guilds:
            print("Checking guilds...")
            search = sq.search_id(self.conn, self.server_table, "server_id", guild.id)
            if not search:
                info = copy.copy(server_default)
                info[0] = guild.name
                info[1] = guild.id
                sq.add_to_table(self.conn, self.server_table, info)
                print(f'Successfully added new guild: {guild.name} with ID {guild.id}.') 
            else:
                cur_info = search[0]
                config_check = await CustomBotClient.std_dicts(json.loads(server_default_config), json.loads(cur_info[3])) #checks the server's config for any settings to be removed/added.
                if config_check != 0:
                    sq.update_value(self.conn, self.server_table, "server_id", guild.id, "config", json.dumps(config_check))
                    print(f"Guild '{guild.name}' server config was missing or had extra parameters and has been standardized.")
                if cur_info[1] != guild.name: #update guild names if any changed.
                    sq.update_value(self.conn, self.server_table, "server_id", guild.id, "server", guild.name)
                    print(f"Guild '{guild.name}' name has been updated in database.") 
                else:
                    print(f"Guild '{guild.name}' with ID {guild.id} has been verified.")

            print(f"Checking members in '{guild.name}' server...")
            for member in guild.members:
                search = sq.search_id(self.conn, self.main_table, "uid", member.id)
                if not search:
                    userinfo = copy.copy(user_default)
                    #EDIT THIS IF COLUMNS ADDED/DELETED
                    userinfo[0] = member.name
                    userinfo[1] = member.id
                    sq.add_to_table(self.conn, self.main_table, userinfo)
                    print(f"Successfully added new member: {member.name} with ID {str(member.id)}.")
                elif search[0][1] != member.name:
                    sq.update_value(self.conn, self.main_table, "uid", member.id, "user", member.name)
                    print(f"Name of member {member.name} with ID {member.id} was updated in the database.")
                else:
                    print(f"{member.name} of ID {member.id} in '{guild.name}' guild has been verified.")
        
        print('\n ---------- Database initialized. ---------- \n')
        

    
