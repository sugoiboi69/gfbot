from discord.ext import commands
import discord



class MyHelp(commands.MinimalHelpCommand):
    async def send_bot_help(self, mapping):
        avail_categories = {}
        embed = discord.Embed(title="Help", description="Use `;help [command]` for more info on a command.\n")
        embed.add_field
        for cog, commands in mapping.items():
           command_signatures = [self.get_command_signature(c) for c in commands]
           if command_signatures:
                cog_name = getattr(cog, "qualified_name", "No Category")
                category = getattr(cog, "description", "No Category")
                if category == 'No Category': continue
                if category in avail_categories.keys():
                    if cog_name in avail_categories[category].keys():
                        avail_categories[category][cog_name]+=str("\n".join(command_signatures))+"\n"
                    else:
                        print('lol')
                        avail_categories[category][cog_name] = str("\n".join(command_signatures))+"\n"
                else:
                    avail_categories[category] = {str(cog_name): str("\n".join(command_signatures))+"\n"}

        for category in avail_categories.keys():
            string=''
            for cog in avail_categories[category]:
                string += f"**{cog}**: \n {avail_categories[category][cog]} \n"
            embed.add_field(name=f"__**{category}**__: ", value=string, inline=True)

        channel = self.get_destination()
        await channel.send(embed=embed)
    
    async def send_command_help(self, command):
        embed = discord.Embed(title=self.get_command_signature(command))
        embed.add_field(name="Help", value=command.help)
        alias = command.aliases
        if alias:
            embed.add_field(name="Aliases", value=", ".join(alias), inline=False)
        channel = self.get_destination()
        await channel.send(embed=embed)


