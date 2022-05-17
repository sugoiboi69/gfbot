from discord.ext import commands
from discord.ext import tasks
import osu.api_functions.api as osu #for some reason, we need to import it like we're doing so from the main function?
import sqlol.disql as sq #for some reason, we need to import it like we're doing so from the main function?
import discord
import json
import asyncio

class BN_Check(commands.Cog, name='osu! BN Information.'):
    def __init__(self, bot):
        self.bot = bot
        self.announce_changes.start()
        self.conn = self.bot.conn


    @staticmethod
    async def bn_compare(): #obtains old bn info from local file; if none found, create the file with new info from the API.
        try:
            with open("bn_info.json", "r") as f:
                old_info = json.load(f)
                new_info = osu.bn_info(1)
                change_info = []
                """
                finds each BN in old_info using their ID, and checks their status compared to in new_info; if the status changed, append to changelist. 
                if the BN wasn't found, he was removed, so add that as a status.
                if a new BN was found, add that as a status.
                """
                
                for a in old_info: #adds status changes and those who were removed.
                    found = 0
                    for b in new_info:
                        if a[1]==b[1]:
                            found = 1
                            if a[2]==b[2]: pass
                            else: change_info.append([b, a[2]+' -> '+b[2]])
                    if found == 0:
                        change_info.append([a, 'removed.'])
                
                for b in new_info: #checks BNs in new_info for new additions.
                    found = 0
                    for a in old_info:
                        if a[1]==b[1]: found = 1
                    if found == 0:
                        change_info.append([b, 'added.'])
                
                with open("bn_info.json", "w") as f:
                    json.dump(new_info, f, indent=2)
                
                return change_info
        
        except:
            with open("bn_info.json", "w") as f:
                json.dump(osu.bn_info(1), f, indent=2)
                print("bn_info.json wasn't found; obtained newest BN information and created the file.")
                return None


    @commands.command(name='bn', help='Shows osu! BNs and their modding statuses.')
    async def bn(self, ctx):
        info = osu.bn_info(0)
        embed = discord.Embed(title='Current osu! Beatmap Nominators')
        embed.set_thumbnail(url='https://bn.mappersguild.com/images/cat.png')
        str1 = ''
        for i in info['open']:
            str1 = str1 +  i[0] + ', '
        str1 = str1[:-2]
        embed.add_field(name='Open', value=str1, inline=True)

        str2 = ''
        for i in info['closed']:
            str2 = str2 + i[0] + ', '
        str2 = str2[:-2]

        embed.add_field(name='Closed', value=str2, inline=True)

        str3 = ''
        for i in info['unknown']:
            str3 = str3 + i[0] + ', '
        str3 = str3[:-2]
        embed.add_field(name='Unknown', value=str3, inline=True)
        await ctx.send(embed=embed)        


    @tasks.loop(seconds=60, count=None)
    async def announce_changes(self): #announces in every server which enables this function, if there are status changes for any BNs.
        changes = await BN_Check.bn_compare()
        if changes == []:
            print('No changes found in BN info.')
        else:
            printstr = ''
            embed = discord.Embed(title="Changes in osu! Beatmap Nominator Statuses")
            embed.set_thumbnail(url='https://bn.mappersguild.com/images/cat.png')
            string = changes[0][0][0] + ": " + changes[0][1]
            print(f"Announcing BN status changes: \n{string}")
            embed.add_field(name="The below changes were found:", value=string)

            for guild in self.bot.guilds:
                guild_info = json.loads(sq.search_id(self.conn, self.bot.server_table, 'server_id', guild.id)[0][3])
                if guild_info['bn_ping'] == 1:
                    for channel in guild.channels:
                        if channel.id == guild_info['bn_ping_channel']:
                            await channel.send(embed=embed)
                            printstr = printstr + guild.name + ': ' + channel.name + '\n'
                            break
                    else:
                        print(f"couldn't send message to guild {guild.name}; sending an error message to any available channel there.")
                        for channel in guild.channels:
                            try:
                                await channel.send("Couldn't send a BN information announcement even though it was enabled in this server. Try setting a channel again.")
                                break
                            except:
                                pass
                        else:
                            print(f"Could not send a BN status announcement or error message to {guild.name}.")
                    
                    print(f"Managed to send a BN status announcement to the following server's channel: \n{printstr}")


    @commands.command(name='bnannounce', help="Enable/disable/set the channel for announcing whenever an osu! BN's status changes.")
    @commands.has_permissions(administrator=True)
    async def bnannounce(self, ctx):
        def check(reaction, user):
            return user == ctx.message.author and str(reaction.emoji) in ["✔️", "❌"]

        guild_info = json.loads(sq.search_id(self.conn, self.bot.server_table, 'server_id', ctx.guild.id)[0][3]) #get the config of the current guild.
        if guild_info['bn_ping']!=0:
            if guild_info['bn_ping_channel']==ctx.channel.id:
                msg = await ctx.send("Remove this channel from getting BN status announcements?")
                await msg.add_reaction("✔️")
                await msg.add_reaction("❌")
                try:
                    reaction, user = await self.bot.wait_for('reaction_add', timeout=60, check=check)
                    if reaction.emoji == "✔️":
                        guild_info['bn_ping'] = 0
                        sq.update_value(self.conn, 'server','server_id', ctx.guild.id, 'config', json.dumps(guild_info))
                        await ctx.send("Removed the channel.")
                    elif reaction.emoji == "❌":
                        await ctx.send("Understood.")
                        pass
                except asyncio.TimeoutError:
                    await ctx.send("Timed out.")
                
            else:
                msg = await ctx.send("Set this channel instead for BN status announcements?")
                await msg.add_reaction("✔️")
                await msg.add_reaction("❌")
                try:
                    reaction, user = await self.bot.wait_for('reaction_add', timeout=60, check=check)
                    if reaction.emoji == "✔️":
                        guild_info['bn_ping_channel'] = ctx.channel.id
                        sq.update_value(self.conn, 'server','server_id', ctx.guild.id, 'config', json.dumps(guild_info))
                        await ctx.send("Channel has been set.")
                    elif reaction.emoji == "❌":
                        await ctx.send("Understood.")
                except asyncio.TimeoutError: 
                    await ctx.send("Timed out.")

        else:
            msg = await ctx.send("Do you want to enable BN status announcements in this channel?")
            await msg.add_reaction("✔️")
            await msg.add_reaction("❌")
            try:
                reaction, user = await self.bot.wait_for('reaction_add', timeout=60, check=check)
                if reaction.emoji == "✔️":
                    guild_info['bn_ping'] = 1
                    guild_info['bn_ping_channel'] = ctx.channel.id
                    sq.update_value(self.conn, 'server','server_id', ctx.guild.id, 'config', json.dumps(guild_info))
                    await ctx.send("Enabled this channel.")
                elif reaction.emoji == "❌":
                    await ctx.send("Understood.")
            except asyncio.TimeoutError: 
                await ctx.send("Timed out.")




    
