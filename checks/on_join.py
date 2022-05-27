from discord.ext import commands
import sqlol.disql as sq
from clients.bot_vars import bot_vars
from checks.db_checker import DBCheck
import json
import copy

"""
this cog just ensures that new servers and members are added to the db upon joining.
most of the code is just copied over from db_checker.
will have to write another cog for greetings, if needed.
"""

class On_Join(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.conn = bot_vars.conn
        self.main_table = bot_vars.main_table
        self.server_table = bot_vars.server_table
        self.server_default = bot_vars.server_default

    @commands.Cog.listener()
    async def on_member_join(self, member): #adds a new member.
        if not member.bot:
            print(f"A new member, {member.name} with ID {member.id}, joined. Adding them to the database...")
            userinfo = copy.copy(bot_vars.user_default)
            userinfo[0] = member.name
            userinfo[1] = str(member.id)
            temp = json.loads(userinfo[3])
            for x in member.mutual_guilds:
                temp['servers'].append(x.id)
            userinfo[3] = json.dumps(temp)
            sq.add_to_table(self.conn, self.main_table, userinfo)
            print(f"Successfully added new member: {member.name} with ID {str(member.id)}.")
    
    
    @commands.Cog.listener()
    async def on_join_guild(self, guild):
        print(f"Joined a new guild, {guild.name}. Adding guild and members to database...")
        server_default_config = json.dumps(bot_vars.config)
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
