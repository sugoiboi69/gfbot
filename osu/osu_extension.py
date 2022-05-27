from discord.ext import commands
from osu.bn import BN_Check
from osu.profiles import Profiles

def setup(bot):
    bot.add_cog(BN_Check(bot))
    bot.add_cog(Profiles(bot))