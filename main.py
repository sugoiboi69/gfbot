
import os
import random
import discord
import disql as sq
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
intents = discord.Intents.default()
intents.members = True
TOKEN = os.getenv('DISCORD_TOKEN')
bot = commands.Bot(command_prefix=';', intents=intents)

#connect to disc table in disc.db; attempt to create else just connect
conn = sq.create_connection(r"C:\Users\Hisham\Documents\GitHub\gfbot\disc.db")
main_table = "disc"
sq.create_table(conn, main_table)





### initialize the bot; add unadded members to the database with 0 dollars.
@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')
    for guild in bot.guilds:
        print(f"checking members in {guild.name}...")
        for member in guild.members:
            if not sq.search_id(conn, main_table, member.id):
                userinfo = [member.name, member.id, '0', '']
                sq.add_to_table(conn, main_table, userinfo)
                print(f"successfully added new member: {member.name} with ID {str(member.id)}.")
            
            else:
                print(f"{member.name} of ID {member.id} has already been added.")


@bot.event #add all on_message responses here
async def on_message(message):
    if message.author == bot.user:
        return

    if message.content == 'gf':
        await message.channel.send("what do u want lol")

    await bot.process_commands(message)


@bot.command(name='create-channel')
@commands.has_role('admin')
async def create_channel(ctx, channel_name='real-python'):
    guild = ctx.guild
    existing_channel = discord.utils.get(guild.channels, name=channel_name)
    if not existing_channel:
        print(f'Creating a new channel: {channel_name}')
        await guild.create_text_channel(channel_name)


@bot.command(name='99', help = '99?')
async def nine_nine(ctx):
    await ctx.send('one hunnid')


@bot.command(name='roll', help='Simulates rolling dice.')
async def roll(ctx, number_of_dice: int, number_of_sides: int):
    dice = [
        str(random.choice(range(1, number_of_sides + 1)))
        for _ in range(number_of_dice)
    ]
    await ctx.send(', '.join(dice))


@bot.command(name='osu', help = 'Connect your osu! account.')
async def osu(ctx, option: str, username: str):
    if option == "connect":
        sq.update_value(conn, main_table, ctx.author.id, "osu_name", username)
        await ctx.send(f"{username} added as your osu! username, {ctx.author.name}.")
    
    if option == ""


bot.run(TOKEN)
