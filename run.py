from clients.bot import Bot
from clients.bot_vars import bot_vars
from economy.economy import Economy
from responses.greetings import Greetings

from checks.error import CommandErrHandler
#from checks.logger import Logger
from checks.db_checker import DBCheck

from osu.bn import BN_Check
from osu.profiles import Profiles

import sqlol.disql as sq
import discord
import os
from dotenv import load_dotenv
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

"""
this script runs the bots and adds all the cogs. bot is obtained from 'bot' folder, while
cogs are obtained from other folders.
"""

def main():

    #initialize bot stuff
    print("\n ---------- Starting up bot ... ---------- \n")
    token = TOKEN
    intents = discord.Intents.default()
    intents.members = True

    bot = Bot(
        command_prefix=';',
        intents=intents,
    )
    bot.conn = bot_vars.conn
    bot.main_table = bot_vars.main_table
    bot.server_table = bot_vars.server_table

    #add all the cogs LOL
    bot.add_cog(Greetings(bot))
    bot.add_cog(CommandErrHandler(bot))
    #bot.add_cog(Logger(bot))
    bot.add_cog(BN_Check(bot))
    bot.add_cog(Profiles(bot))
    bot.add_cog(DBCheck(bot))
    bot.add_cog(Economy(bot))

    bot.run(token)

if __name__ == '__main__':
    main()