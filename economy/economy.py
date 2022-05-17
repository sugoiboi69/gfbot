from discord.ext import commands
from clients.bot_vars import bot_vars
import economy.addsub as money
import discord
import asyncio

class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='balance')
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def balance(self, ctx: commands.Context, user: discord.Member = None):
        if user is None:
            user = ctx.author
        if user.bot:
            await ctx.send("Bots don't have money.")
        amt = money.bal(user.id)
        await ctx.send(f"{user.display_name} currently has ${amt}.")
    
    @commands.command(name='send')
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def send(self, ctx:commands.Context, user:discord.Member=None, amount:int=0):
        cur = money.bal(ctx.author.id)
        if int <= 0:
            await ctx.send("You must enter an amount greater than zero to send.")
        elif user == None:
            await ctx.send("Please mention the user you would like to send money to.")
        elif user == ctx.author.id:
            await ctx.send("You can't send yourself money.")
        elif user.bot:
            await ctx.send("You can't send money to a bot.") 
        elif cur < amount:
            await ctx.send(f"You only have ${cur}; you need ${amount-cur} more to send that amount.")

        else:
            def check(reaction, user):
                return user == ctx.message.author and str(reaction.emoji) in ["✔️", "❌"]
            msg = await ctx.send(f"Are you sure you want to send ${amount} to {user.display_name}?")
            await msg.add_reaction("✔️")
            await msg.add_reaction("❌")
            try:
                reaction, user = await self.bot.wait_for('reaction_add', timeout=60, check=check)
                if reaction.emoji == "✔️":
                    money.sub(ctx.author.id, amount)
                    money.add(user.id, amount)
                    await ctx.send("Successfully sent.")
                elif reaction.emoji == "❌":
                    await ctx.send("Understood.")
                    pass
            except asyncio.TimeoutError:
                    await ctx.send("Timed out.")
    
    @commands.command(name='daily')
    async def daily(self, ctx:commands.Context):
        pass

    
    @commands.command(name='request')
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def request(self, ctx:commands.Context, amount: int=0, user: discord.Member=None):
        if int <= 0:
            await ctx.send("You must enter an amount greater than zero to send.")
        elif user == None:
            await ctx.send("Please mention the user you would like to request money from.")
        elif user == ctx.author.id:
            await ctx.send("You can't request yourself money.")
        elif user.bot:
            await ctx.send("You can't request money from a bot.")
        
        else:
            #have to write this out.
            pass


        
        
    #@commands.command(name='daily')
    #@commands.cooldown(1, 30, commands.BucketType.user) 

