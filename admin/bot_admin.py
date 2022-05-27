from discord.ext import commands
from random import randint
import discord
import json

class Admin(commands.Cog, name="Admin", description="Admin"):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name='addadmin')
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def addadmin(self, ctx, user:discord.User=None):
        if user==None:
                await ctx.send('Please mention a user.')
                return
        if user.id in self.bot.bot_config['bot_admins']:
            await ctx.send(f'{user.name} is already an admin.', delete_after=5)
            return
        if str(ctx.author.id) not in self.bot.bot_config['bot_admins']:
            await ctx.send('You are not a bot admin. To bypass, enter the code printed in the console.', delete_after=5)
            code = randint(100000, 999999)
            print(code)
            def check(m):
                return m.author==ctx.author and m.content.isdigit()
            try:
                reply = await self.bot.wait_for('message', timeout=10, check=check)
                if int(reply.content) == code:
                    self.bot.bot_config['bot_admins'].append(ctx.author.id)
                    with open("config.json", "w") as f:
                        json.dump(self.bot.bot_config, f, indent=2)
                    await ctx.send(f"Code verified; new admin {user.name} added.")
                    await reply.delete()
                else:
                    await ctx.send("Wrong code.", delete_after=5)
                    await reply.delete()
                    return
            except:
                await ctx.send("Ran out of time.", delete_after=5)
                return

        else:
            self.bot.bot_config['bot_admins'].append(ctx.author.id)
            with open("config.json", "w") as f:
                    json.dump(self.bot.bot_config, f, indent=2)
            await ctx.send(f"New admin {user.name} added.")