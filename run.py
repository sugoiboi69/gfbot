######################
from clients.bot import Bot
from clients.bot_vars import bot_vars
from clients.help import MyHelp
import discord
import json
import copy
import os
from dotenv import load_dotenv
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

"""
use this to start the bot; it checks config file, starts the bot and adds the cogs.
cogs are loaded via their respective extensions for neatness.
to add/delete a cog, do so from the extensions themselves, which are in the folders.
"""
def set_config(): #this function creates bot config file based on user preference.
        print("Now setting the bot's settings.")
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

        print("\nFinished setting the configuration for the bot. Here are your settings: ")
        for key in new_config.keys():
            print(str(key) + ": " + str(new_config[key]))
        with open("config.json", "w") as f:
            json.dump(new_config, f, indent=2)

def main():
    #initialize bot stuff
    print("\n ---------- Starting up bot ... ---------- \n")
    token = TOKEN
    intents = discord.Intents.default()
    intents.members = True

    ###checks the bot config against default settings, or creates a new config if one isn't found
    try:
        change=0
        with open("config.json", "r") as f:
            bot_config = json.load(f)
        print("Checking current bot configuration settings: ")
        for key in bot_config.keys():   
            if key not in bot_vars.bot_config.keys():
                change=1
                print(f"Deleting setting '{str(key)}: {str(bot_config[key])}'.")
                bot_config.pop(key)
            elif not bot_config[key]:
                bot_config[key] = input(f"The setting '{key}' had no value. Please input its setting (type {type(key).__name__}): ")
                change=1
            else:
                print(str(key) + ": " + str(bot_config[key]))
        for key in bot_vars.bot_config.keys():
            if key not in bot_config.keys():
                bot_config[key] = input(f"The setting for '{key}' was missing. Please input its setting (type {type(key).__name__}): ")
                change=1
        if change:
            print("Saving changes to config...")
            with open("config.json", "w") as f:
                json.dump(bot_config, f, indent=2)
    except:
        print("Seems there was no config file found. Creating one...")
        set_config()
        with open("config.json", "r") as f:
            bot_config = json.load(f)
            
    print('\n ---------- Bot configuration loaded. ---------- \n')
        
    #starts the bot
    bot = Bot(
        command_prefix=bot_config['command_prefix'],
        intents=intents,
        help_command=MyHelp()
    )
    bot.conn = bot_vars.conn
    bot.main_table = bot_vars.main_table
    bot.server_table = bot_vars.server_table
    
    bot.load_extension('checks.checks_and_errors_extension')#error and checking cogs
    bot.load_extension('osu.osu_extension') #osu cogs
    bot.load_extension('economy.economy_and_games_extension') #economy/games cogs
    bot.load_extension('admin.admin_extension') #admin cogs
    bot.run(token)

if __name__ == '__main__':
    main()