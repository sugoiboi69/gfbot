from discord.ext import commands
from economy.economy import Economy
from economy.games.wordle import Wordle

def setup(bot):
    bot.add_cog(Economy(bot))
    bot.add_cog(Wordle(bot))