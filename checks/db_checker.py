from discord.ext import commands
from discord.ext import tasks
from datetime import datetime
from clients.bot_vars import bot_vars
import sqlol.disql as sq 
import json
import copy

class DBCheck(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.dbcheck.start()
        self.conn = bot_vars.conn
        self.main_table = bot_vars.main_table
        self.server_table = bot_vars.server_table
        self.server_default = bot_vars.server_default
    
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

    
    @tasks.loop(seconds=120, count=None)
    async def dbcheck(self):

        """
        this task loops every __ minutes to check that the database contains all the necessary columns + guild and member info.
        it also ensures that the names are correct, and that the guild config is standardized (in the case that we change the amount of parameters in the config file).
        if any guild/member is not in database, fetch default database info from bot_vars and add necessary info (id, name, mutual servers, etc), then add it to the database.
        """
        
        await self.bot.wait_until_ready()
        print('Performing database check ...')
        server_default_config = json.dumps(bot_vars.config)

        server_columns = sq.get_columns(self.conn, self.server_table) #check that the tables have all the required columns.
        for column in bot_vars.server_cols:
            if column not in server_columns:
                print(f"Server database was missing column '{column}'; adding it now...")
                sq.add_column(self.conn, self.server_table, column, bot_vars.server_cols_type[bot_vars.server_cols.index(column)])                
        user_columns = sq.get_columns(self.conn, self.main_table)
        for column in bot_vars.user_cols:
            if column not in user_columns:
                print(f"User database was missing column '{column}'; adding it now...")
                sq.add_column(self.conn, self.main_table, column, bot_vars.user_cols_type[bot_vars.user_cols.index(column)])


        for guild in self.bot.guilds: #checks guilds are in db + their config is standardized.
            search = sq.search_id(self.conn, self.server_table, "server_id", guild.id)
            if not search:
                info = copy.copy(bot_vars.server_default)
                info[0] = guild.name
                info[1] = guild.id
                sq.add_to_table(self.conn, self.server_table, info)
                print(f'Successfully added new guild: {guild.name} with ID {guild.id}.') 
            else:
                cur_info = search[0]
                config_check = await DBCheck.std_dicts(json.loads(server_default_config), json.loads(cur_info[3])) #checks the server's config for any settings to be removed/added.
                if config_check != 0:
                    sq.update_value(self.conn, self.server_table, "server_id", guild.id, "config", json.dumps(config_check))
                    print(f"Guild '{guild.name}' server config was missing or had extra parameters and has been standardized.")
                if cur_info[1] != guild.name: #update guild names if any changed.
                    sq.update_value(self.conn, self.server_table, "server_id", guild.id, "server", guild.name)
                    print(f"Guild '{guild.name}' name has been updated in database.") 
                else:
                    pass

            
            for member in guild.members:
                if member.bot:
                    continue
                search = sq.search_id(self.conn, self.main_table, "uid", member.id)
                if not search:
                    userinfo = copy.copy(bot_vars.user_default)
                    userinfo[0] = member.name
                    userinfo[1] = str(member.id)
                    temp = json.loads(userinfo[3])
                    for x in member.mutual_guilds:
                        temp['servers'].append(x.id)
                    userinfo[3] = json.dumps(temp)
                    sq.add_to_table(self.conn, self.main_table, userinfo)
                    print(f"Successfully added new member: {member.name} with ID {str(member.id)}.")
                elif search[0][1] != member.name:
                    sq.update_value(self.conn, bot_vars.main_table, "uid", member.id, "user", member.name)
                    print(f"Name of member {member.name} with ID {member.id} was updated in the database.")
                else:
                    user_servers = json.loads(search[0][4]) #checks that all mutual guilds are added.
                    change = 0
                    for x in member.mutual_guilds:
                        if x.id not in user_servers['servers']:
                            user_servers['servers'].append(x)
                            change = 1
                    
                    if change:
                        sq.update_value(self.conn, bot_vars.main_table, "uid", member.id, "servers", json.dumps(user_servers))





        print("Database verified.")
