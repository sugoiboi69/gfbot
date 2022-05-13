from discord.ext import commands
import osu.api_functions.api as osu #for some reason, we need to import it like we're doing so from the main function?
import datetime as dt
import discord

class Profiles(commands.Cog, name='osu_profiles'):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name='mapper', help='Shows your mapping profile on osu!')
    async def mapper(self, ctx, username:str):
        if not username:
            await ctx.send("fucking idiot")
        try:
            info = osu.mapper(username)
            if info == 0:
                await ctx.send(f"Player called {username} wasn't found or had no uploaded maps.")
                return
            
            total = info["mapsets_rpgl"][0]+info["mapsets_rpgl"][1]+info["mapsets_rpgl"][2]+info["mapsets_rpgl"][3]
            embed=discord.Embed(title=info['username'], url="https://osu.ppy.sh/users/"+str(info['id']), description=f"Mapper for {info['oldest_ymd'][0]} years, {info['oldest_ymd'][1]} months, and {info['oldest_ymd'][2]} days.", color=0x0080ff)
            embed.set_thumbnail(url=info['avatar_url'])
            embed.add_field(name="Subs", value=info['followers'], inline=True)
            embed.add_field(name=f"Total Maps: {total}", value=f"Ranked: {info['mapsets_rpgl'][0]}, Pending: {info['mapsets_rpgl'][1]}, Graved: {info['mapsets_rpgl'][2]}, Loved: {info['mapsets_rpgl'][3]} ", inline=False)
            embed.add_field(name=f"Latest Map ({info['newest'][2]}):", value = "["+ info['newest'][0]+"]("+info['newest'][1]+")", inline=True)
            embed.set_image(url=info["newest"][3])
            embed.set_footer(text=f"requested on {str(dt.date.today())}")
            await ctx.send(embed=embed)
    
        except Exception as e:
            print(e)
            await ctx.send("Ran into an error.")
