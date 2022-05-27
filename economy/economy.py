from discord.ext import commands
import datetime
from clients.bot_vars import bot_vars
import economy.addsub as money
import sqlol.disql as sq
import discord
import asyncio
import json
import math



class Economy(commands.Cog, name='Money', description='Economy'):
    def __init__(self, bot):
        self.bot = bot
        self.conn = bot_vars.conn
        self.main_table = bot_vars.main_table
        self.server_table = bot_vars.server_table

    @commands.command(name='balance',
                    help = """**Check a user's bank balance.** Takes the following arguments:
                    
                    **user:** a Discord user to check; else, check your own balance.
                    """)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def balance(self, ctx: commands.Context, user: discord.Member = None):
        if user is None:
            user = ctx.author
        if user.bot:
            await ctx.send("Bots don't have money.")
        else:
            amt = money.bal(user.id)
            await ctx.send(f"{user.display_name} currently has ${amt}.")
    

    @commands.command(name='send',
                    help = """**Send money to another person in the server.** Takes the following arguments:

                    **recipient:** The person to send money to.
                    **amount:** The amount to send.
                    """)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def send(self, ctx:commands.Context, recipient:discord.Member=None, amount:int=0):
        cur = money.bal(ctx.author.id)
        if recipient == None:
            await ctx.send("Please mention the user you would like to send money to.")
        elif amount < 1:
            await ctx.send("You must enter an amount greater than zero to send.")
        elif recipient.id == ctx.author.id:
            await ctx.send("You can't send yourself money.")
        elif recipient.bot:
            await ctx.send("You can't send money to a bot.") 
        elif cur < amount:
            await ctx.send(f"You only have ${cur}; you need ${amount-cur} more to send that amount.")
        else:
            def check(reaction, user):
                return user == ctx.message.author and str(reaction.emoji) in ["✔️", "❌"]
            msg = await ctx.send(f"Are you sure you want to send ${amount} to {recipient.display_name}?")
            await msg.add_reaction("✔️")
            await msg.add_reaction("❌")
            try:
                reaction, user = await self.bot.wait_for('reaction_add', timeout=60, check=check)
                if reaction.emoji == "✔️":
                    money.sub(ctx.author.id, amount)
                    money.add(recipient.id, amount)
                    await ctx.send("Successfully sent.")
                elif reaction.emoji == "❌":
                    await ctx.send("Understood.")
                    pass
            except asyncio.TimeoutError:
                    await ctx.send("Timed out.")
    

    @commands.command(name='freebie',
                    help = "**Get free money!**")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def freebie(self, ctx:commands.Context):
        last_freebie = sq.search_id(self.conn, self.main_table, "uid", ctx.author.id)[0][5]
        if last_freebie == '':
            money.add(ctx.author.id, self.bot.bot_config['freebie_amount'])
            await ctx.send(f"Your freebie of ${self.bot.bot_config['freebie_amount']} has been sent! Wait another {self.bot.bot_config['freebie_cooldown_hours']} hours for the next freebie.")
            sq.update_value(self.conn, self.main_table, "uid", ctx.author.id, "last_freebie", datetime.datetime.now().strftime(f"%d/%m/%Y %H:%M:%S"))
        else:
            try:
                next_avail = datetime.datetime.strptime(last_freebie, f"%d/%m/%Y %H:%M:%S") + datetime.timedelta(hours=self.bot.bot_config['freebie_cooldown_hours'])
                if next_avail > datetime.datetime.now():
                    minutes = math.floor((next_avail-datetime.datetime.now()).total_seconds() / 60)
                    hours = divmod(minutes, 60)
                    await ctx.send(f"Not yet! Your next freebie is in {hours[0]} hours and {hours[1]} minutes.")
                else:
                    money.add(ctx.author.id, self.bot.bot_config['freebie_amount'])
                    await ctx.send(f"Your freebie of ${self.bot.bot_config['freebie_amount']} has been sent! Wait another {self.bot.bot_config['freebie_cooldown_hours']} hours for the next freebie.")
                    sq.update_value(self.conn, self.main_table, "uid", ctx.author.id, "last_freebie", datetime.datetime.now().strftime(f"%d/%m/%Y %H:%M:%S"))
            except Exception as e:
                    print(e)
                    money.add(ctx.author.id, self.bot.bot_config['freebie_amount'])
                    await ctx.send(f"Your freebie of ${self.bot.bot_config['freebie_amount']} has been sent! Wait another {self.bot.bot_config['freebie_cooldown_hours']} hours for the next freebie.")
                    sq.update_value(self.conn, self.main_table, "uid", ctx.author.id, "last_freebie", datetime.datetime.now().strftime(f"%d/%m/%Y %H:%M:%S"))

    
    @commands.command(name='request',
                    help = """**Request money from a person; a request must be accepted within 5 minutes.** Takes the following arguments: 

                    **amount:** The amount of money to request.
                    **user:** A Discord user to request from.
                    """)
    @commands.cooldown(1, 300, commands.BucketType.user)
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

