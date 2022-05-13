from discord.ext import commands
from discord.ext import tasks
import sqlol.disql as sq 
from clients.bot_vars import bot_vars
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

    
    @tasks.loop(minutes=5, count=None) #verifies database info is correct
    async def dbcheck(self):
        print('Performing database check ...')
        server_default_config = json.dumps(bot_vars.config)
        for guild in self.bot.guilds:
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
                    #print(f"Guild '{guild.name}' with ID {guild.id} has been verified.")

            #print(f"Checking members in '{guild.name}' server...")
            for member in guild.members:
                search = sq.search_id(self.conn, self.main_table, "uid", member.id)
                if not search:
                    userinfo = copy.copy(bot_vars.user_default)
                    #EDIT THIS IF COLUMNS ADDED/DELETED
                    userinfo[0] = member.name
                    userinfo[1] = member.id
                    sq.add_to_table(self.conn, self.main_table, userinfo)
                    print(f"Successfully added new member: {member.name} with ID {str(member.id)}.")
                elif search[0][1] != member.name:
                    sq.update_value(self.conn, bot_vars.main_table, "uid", member.id, "user", member.name)
                    print(f"Name of member {member.name} with ID {member.id} was updated in the database.")
                else:
                    pass
                    #print(f"{member.name} of ID {member.id} in '{guild.name}' guild has been verified.")
        print("Database verified.")
