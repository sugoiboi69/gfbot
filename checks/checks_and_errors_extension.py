from discord.ext import commands
from checks.error import CommandErrHandler
#from checks.logger import Logger
from checks.db_checker import DBCheck
from checks.on_join import On_Join

def setup(bot):
    #bot.add_cog(Greetings(bot))
    bot.add_cog(CommandErrHandler(bot))
    bot.add_cog(DBCheck(bot))
    bot.add_cog(On_Join(bot))
    #bot.add_cog(Logger(bot))