from discord.ext import commands
from discord.ext import tasks
import osu.api_functions.api as osu #for some reason, we need to import it like we're doing so from the main function?
import sqlol.disql as sq #for some reason, we need to import it like we're doing so from the main function?
import os
import datetime as dt
import discord
import json
import asyncio

bn_site_filepath = os.getcwd()+r"\osu\info\bn_info.json"
forum_q_filepath = os.getcwd()+r"\osu\info\forum_q.json"
gform_filepath = os.getcwd()+r"\osu\info\gform.json"

class BN_Check(commands.Cog, name='BN Info', description = 'osu!'):
    def __init__(self, bot):
        self.bot = bot
        self.announce_changes.start()
        self.conn = self.bot.conn


    @staticmethod
    def bn_compare(): #obtains old bn info from local file; if none found, create the file with new info from the API.
        try:
            with open(bn_site_filepath, "r") as f:
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
                
                with open(bn_site_filepath, "w") as f:
                    json.dump(new_info, f, indent=2)
                
                return change_info
        
        except:
            with open(bn_site_filepath, "w") as f:
                json.dump(osu.bn_info(1), f, indent=2)
                print("bn_info.json wasn't found; obtained newest BN information and created the file.")
                return None


    @commands.command(name='bn', help='**Shows osu! BN statuses.**')
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
    async def announce_changes(self):
        """
        announces in every server which enables this function, if there are status changes for any BNs.
        *changes* checks the BN site, *forum_changes* checks the forum mod queues, *gform_changes* checks the added google forms.
        """
        await self.bot.wait_until_ready()
        changes = BN_Check.bn_compare()
        forum_changes = osu.forum_queue_info()

        try:
            gform_changes = {}
            with open(gform_filepath, "r") as f:
                last_gform_info = json.load(f)   
            if last_gform_info:
                x=[]
                for gform in last_gform_info.keys():
                    x.append(str(gform))
                new_gform_info = osu.gform_info(x)
                for gform in new_gform_info.keys():
                    if new_gform_info[gform]['inputs']==0 and last_gform_info[gform]['inputs']>0:
                        gform_changes[gform] = {'change': 'might have just closed.', 'name': last_gform_info[gform]['name']}                       
                    elif new_gform_info[gform]['inputs']>0 and last_gform_info[gform]['inputs']==0:
                        gform_changes[gform] = {'change': 'might have just opened.', 'name': last_gform_info[gform]['name']}
                    elif new_gform_info[gform]['inputs'] != last_gform_info[gform]['inputs']:
                        gform_changes[gform] = {'change': 'might have changed format.', 'name': last_gform_info[gform]['name']}
                    last_gform_info[gform]['inputs'] = new_gform_info[gform]['inputs']
                    last_gform_info[gform]['title'] = new_gform_info[gform]['title']
                with open(gform_filepath, "w") as f:
                    json.dump(last_gform_info, f, indent=2)
        except Exception as e:
            print(f"error: {str(e)}")
            with open(gform_filepath, "w") as f:
                json.dump({}, f, indent=2)
            print("gform.json wasn't found; created an empty file, please add some BN forms to check!")

        if changes==[] and forum_changes==None and gform_changes==None:
            print('No changes found in BN info.')
            return

        if forum_changes:
                try:
                    with open(forum_q_filepath, "r") as f:
                        last_forum_q = json.load(f)
                        for modq_id in forum_changes.keys():
                            if modq_id not in last_forum_q:
                                replace_q = []
                                for modq_id in forum_changes.keys():
                                    replace_q.append(modq_id)
                                with open(forum_q_filepath, "w") as f:
                                    json.dump(replace_q, f, indent=2)
                                break
                        else:
                            print("Forum check consistent with last check; no announcement made.")
                            forum_changes = None #ensures that a forum change isn't announced if it was already announced before and stored in the json.
                except:
                    last_forum_q = []
                    for modq_id in forum_changes.keys():
                        last_forum_q.append(modq_id)
                    with open(forum_q_filepath, "w") as f:
                        json.dump(last_forum_q, f, indent=2)
                    print("forum_q.json wasn't found; obtained newest forum queue information and created the file.")
                    last_forum_q = []
                    
        if changes or forum_changes or gform_changes:
            embed = discord.Embed(title="BN Status Announcement")
            embed.set_thumbnail(url='https://bn.mappersguild.com/images/cat.png')

            if changes:
                string = f"**{changes[0][0][0]}**" + ": " + changes[0][1]
                print(f"Announcing BN status changes: \n{string}")
                embed.add_field(name="BN Site: ", value=string, inline=False)
            
            if forum_changes:
                modq_string = ''
                for modq_id in forum_changes.keys():
                    if modq_id not in last_forum_q:
                        timestring = f"{str(forum_changes[modq_id][1].days)} days, {forum_changes[modq_id][1].seconds//3600} hours"
                        modq_string += f"**[{forum_changes[modq_id][0]}](https://osu.ppy.sh/community/forums/topics/{modq_id})** has a new post after {timestring}:\n {forum_changes[modq_id][2]}"+"\n\n"        
                embed.add_field(name="Forum Mod Queues: ", value=modq_string, inline=False)
            
            if gform_changes:
                gform_string = ''
                for gform in gform_changes.keys():
                    gform_string += f"**[{gform_changes[gform]['name']}'s form]({str(gform)})** {gform_changes[gform]['change']}"+"\n"
                embed.add_field(name="Added BN Google Forms: ", value=gform_string, inline=False)

            printstr = ''
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


    @commands.command(name='bnannounce', help="**Enable/disable/set the channel for announcing whenever an osu! BN's status changes.**")
    @commands.has_permissions(administrator=True)
    async def bnannounce(self, ctx):
        def check(reaction, user):
            return user == ctx.message.author and str(reaction.emoji) in ["✔️", "❌"]

        guild_info = json.loads(sq.search_id(self.conn, self.bot.server_table, 'server_id', ctx.guild.id)[0][3]) #get the config of the current guild.
        if guild_info['bn_ping']!=0:
            if guild_info['bn_ping_channel']==ctx.channel.id:
                embed = discord.Embed(title="Remove this channel from getting BN status announcements?")
                msg = await ctx.send(embed=embed)
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
                embed = discord.Embed(title="Set this channel instead for BN status announcements?", description="Information will come from BN website, and BN/NAT forum mod queues that have been revived.")
                msg = await ctx.send(embed=embed)
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
            embed = discord.Embed(title="Do you want to enable BN status announcements in this channel instead?")
            msg = await ctx.send(embed=embed)
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
    

    @commands.command(name='bnform',
                    help = """**Add/remove a BN's Google Form to be status-checked.** Takes the following arguments:
                    
                    **username:** The BN's username.
                    **link**: The link to the Google Form.

                    If both arguments are missing, sends a list of currently checked Google Forms. If the username is 'remove', removes the username's form from the list.  
                    """)
    async def bnform(self, ctx, username:str=None, link:str=None):
        with open(gform_filepath, "r") as f:
                    last_gform_info = json.load(f)
        if not username and not link:
            gform_string = ''
            for gform in last_gform_info.keys():    
                gform_string += f"[{last_gform_info[gform]['name']}]({str(gform)})"
                if last_gform_info[gform]['inputs']>0: gform_string += " **(open)** \n"
                else: gform_string += " **(closed)** \n"
            embed = discord.Embed(title="Currently observed Google Forms: ", description=gform_string)
            embed.set_footer(text="For bot admins: add a Google Form by entering the username and link to be added to this command.")
            await ctx.send(embed=embed)
            return

        if ctx.author.id not in self.bot.bot_config['bot_admins']:
            await ctx.send("Only bot admins can perform this command.", delete_after=3)
            return

        if not username or not link:
            embed = discord.Embed(title="The command requires the BN's **username** and their **Google Form link.**")
            await ctx.send(embed=embed)
            return

        else:
            for gform in last_gform_info.keys():
                if str(gform)==link:
                    embed = discord.Embed(title=f"The link you sent has already been added before, under the name '{last_gform_info[gform]['name']}'.")
                    await ctx.send(embed=embed)
                    return
            try:
                info = osu.gform_info([link])
                info[link]['name'] = username
                last_gform_info[link] = info[link]
                with open(gform_filepath, "w") as f:
                    json.dump(last_gform_info, f, indent=2)
                gform_string = ''
                for gform in last_gform_info.keys():    
                    gform_string += f"[{last_gform_info[gform]['name']}]({str(gform)})"
                    if last_gform_info[gform]['inputs']>0: gform_string += " **(open)** \n"
                    else: gform_string += " **(closed)** \n"
                embed = discord.Embed(title=f"Added {username} to the Google Forms list! Now have:", description=gform_string)
                await ctx.send(embed=embed)
                return        
            except:
                embed = discord.Embed(title="The link given is probably invalid.")
                await ctx.send(embed=embed)
                return





    
