import discord
import sys
import traceback
from discord.ext import commands



class CommandErrHandler(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        """The event triggered when an error is raised while invoking a command.
        Parameters
        ------------
        ctx: commands.Context
            The context used for command invocation.
        error: commands.CommandError
            The Exception raised.
        """

        if isinstance(error, discord.ext.commands.CommandNotFound):
            await ctx.send('retard')
        elif isinstance(error, commands.CheckFailure):
            await ctx.send("You don't have permission to execute this command.")
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"You're on cooldown; try again in {error.retry_after:.2f}s.")
        else:
            print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
            traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)
        
