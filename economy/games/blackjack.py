from discord.ext import commands
import poker

class Blackjack(commands.Cog, name='Blackjack', description='Economy'):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='blackjack',
                    help='Play blackjack!')