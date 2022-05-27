from re import I
from discord.ext import commands
import discord
from asyncio import gather
from clients.bot_vars import bot_vars
import sqlol.disql as sq
import random
import time
import asyncio

#mostly took the code from wordle competition

class Competitor:
    all_competitors = []
    left = []
    win = []
    def __init__(self, user:discord.User):
        Competitor.all_competitors.append(self)
        self.user = user
        self.id = user.id
        self.current_guess = ""
        self.guess_history = []
        self.guesses = []
        self.previous_rounds = []
        self.win = 0
        self.wins = 0
    
    @staticmethod
    def round(guess, word, competitor): #evalutes a competitor's guess and appends it to their guess history.
        if guess == "stop":
            competitor.current_guess = "stop"
            return
        guess_result = ''
        for c in range(5):
            if guess[c] not in word:
                guess_result+=":red_square: "
            elif word[c] == guess[c]:
                guess_result+=":green_square: "
            else:
                guess_result+=":yellow_square: "
        competitor.guess_history.append((guess, guess_result))
        competitor.guesses.append(guess)
        if guess == word:
            competitor.win = 1
            competitor.wins+=1
        return
    
    async def check_for_reply(self, cooldown, word, wordlist, sent): #checks for response
        def check(m):
                if len(m.content) == 5:
                    for competitor in Competitor.all_competitors:
                        if m.author == competitor.user and m.channel == competitor.user.dm_channel and m.author not in sent:
                            if m.content.lower() in wordlist and m.content.lower() not in competitor.guesses:
                                sent.append(m.author)
                                return 1
                        elif m.author in Competitor.left:
                            return 0
                elif m.content.lower() == 'stop':
                    for competitor in Competitor.all_competitors:
                        if m.author == competitor.user and m.author not in sent:
                            competitor.current_guess = "stop"
                            sent.append(m.author)
                            return 1
                return 0
                
        try:
            reply = await self.bot.wait_for('message', timeout=cooldown, check=check)
            for competitor in Competitor.all_competitors:
                if competitor.user == reply.author:
                    Competitor.round(reply.content.lower(), word, competitor)
        except:
            pass
    
    
            


class Wordle(commands.Cog, name='Wordle', description='Economy'):
    def __init__(self, bot):
        self.bot = bot
        self.conn = bot_vars.conn
    
    async def gamestate_eval(self, sent, multi, all_success): 
        embed = discord.Embed(title="Wordle!")
        embed.set_thumbnail(url="https://www.androidfreeware.net/img2/com-TechTreeGames-Wordle.jpg")    
        left_string = ""
        for competitor in Competitor.win:
            current_state_string = ""
            for guess in competitor.guess_history:
                current_state_string += guess[1]+"\n"
            embed.add_field(name=competitor.user.name + " guessed it!", value=current_state_string, inline=True)

        for competitor in Competitor.all_competitors:
            if competitor.user not in sent:
                if multi: await competitor.user.send("You didn't respond this round, so you have been kicked.")
                sq.update_value(self.conn, bot_vars.main_table, "uid", competitor.user.id, "active_game", '')
                Competitor.left.append(competitor)
                Competitor.all_competitors.remove(competitor)   
                left_string += competitor.user.name + ", " #just left
            else:
                current_state_string = ""
                for guess in competitor.guess_history:
                    current_state_string += guess[1]+"\n"
                if competitor.current_guess == "stop":
                    embed_title = competitor.user.name + " has quit."
                    sq.update_value(self.conn, bot_vars.main_table, "uid", competitor.user.id, "active_game", '')
                    Competitor.left.append(competitor)
                    Competitor.all_competitors.remove(competitor) 
                elif competitor.win: #checks who just won, and moves them to the 'win' list.
                    embed_title = competitor.user.name + " just guessed it!"
                    Competitor.all_competitors.remove(competitor)
                    Competitor.win.append(competitor)
                    if not Competitor.all_competitors:
                        all_success = 1
                else: embed_title = competitor.user.name
                if not current_state_string: current_state_string = ":white_large_square: :white_large_square: :white_large_square: :white_large_square: :white_large_square: "
                embed.add_field(name=embed_title, value=current_state_string, inline=True)
        
        for competitor in Competitor.left:
            if competitor.user not in sent:
                current_state_string = ""
                for guess in competitor.guess_history:
                    current_state_string += guess[1]+"\n"
                if not current_state_string: current_state_string = ":white_large_square: :white_large_square: :white_large_square: :white_large_square: :white_large_square: "
                embed.add_field(name=competitor.user.name + " left.", value=current_state_string, inline=True)
        
        return embed, all_success, left_string

  





    #multi/singleplayer wordle game. some code was taken from wordle competition
    @commands.command(name='wordle', 
                        help="""**Starts a single or multiplayer game of Wordle.** Takes the following arguments:

                        **cooldown:** How many seconds allowed for guessing. If not set, defaults to 30 seconds.
                        **multi:** Starts a multiplayer game. If not set, starts a singleplayer game.
                        """)
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def wordle(self, ctx:commands.Context, cooldown=None, multi=None):
        active_game = sq.search_id(self.conn, bot_vars.main_table, "uid", ctx.author.id)[0][6]
        if active_game: #check if in active game
            await ctx.send(f"Seems you're still in a game of {active_game}. Please finish before starting another game.")
            return
        if cooldown==None:
            cooldown=0
        if not isinstance(cooldown, int):
            cooldown=0
            multi='multi'
        cooldown = int(cooldown)


        #gets all the competitors if multi, else just the author. if the author chooses to start another game, it restarts here.
        rounds_played=1
        next_game=1
        while next_game:
            if multi == None:
                if rounds_played==1:
                    Competitor(ctx.author)
                    sq.update_value(self.conn, bot_vars.main_table, "uid", ctx.author.id, "active_game", 'Wordle')  
            else:
                if rounds_played==1:
                    Competitor(ctx.author)
                    sq.update_value(self.conn, bot_vars.main_table, "uid", ctx.author.id, "active_game", 'Wordle')

                def check(reaction, user):
                    if str(reaction.emoji) == "✔️" or str(reaction.emoji) == "❌":
                        for competitor in Competitor.all_competitors:
                            if competitor.user == user:
                                return 0
                    return 1

                embed = discord.Embed(title="React ✔️ to join this Wordle game, or ❌ to leave. Closing in 30 seconds or maximum of 6 players.")
                current_players = ctx.author.name + "\n"
                for competitor in Competitor.all_competitors:
                    if competitor.user != ctx.author: current_players += competitor.user.name + "\n"
                embed.add_field(name="Current players:", value=current_players)
                msg = await ctx.send(embed=embed)
                await msg.add_reaction("✔️")
                await msg.add_reaction("❌")
                timeout = time.time() + 30
                while time.time()<timeout and len(Competitor.all_competitors)<6: #keep looping and checking for reactions until endtime or 6 competitors
                    if 10>timeout-time.time()>9:
                        embed.set_footer(text="10 seconds left!")  
                        await msg.edit(embed=embed)                     
                    try:
                        reaction, user = await self.bot.wait_for('reaction_add', timeout=1, check=check)
                        if str(reaction.emoji) == "✔️":
                            active_game = sq.search_id(self.conn, bot_vars.main_table, "uid", user.id)[0][6]
                            if active_game:
                                await ctx.send(f"{user.name} is still in a game of {active_game} and can't join this one.", delete_after=3) #check if user trying to join is in another active game.
                                continue
                            else:
                                Competitor(user)
                                sq.update_value(self.conn, bot_vars.main_table, "uid", user.id, "active_game", 'Wordle')
                                current_players += user.name + "\n"
                                embed.set_field_at(0, name="Current players: ", value=current_players)
                                await msg.edit(embed=embed)
                        elif str(reaction.emoji) == "❌":
                                for competitor in Competitor.all_competitors:
                                    if competitor.user == user: 
                                        Competitor.all_competitors.remove(competitor)
                                        sq.update_value(self.conn, bot_vars.main_table, "uid", user.id, "active_game", '')
                                        current_players.replace(f"{user.name}\n", "", 1)
                                        embed.set_field_at(0, name="Current players: ", value=current_players)
                                        await msg.edit(embed=embed)
                    except asyncio.TimeoutError:
                        pass
            
            #set up game and send the starting message.
            print("starting wordle game...")
            if multi:
                embed.set_field_at(0, name="Starting game now with following players: ", value=current_players)
                await msg.edit(embed=embed)
            else:
                embed = discord.Embed(title="Starting singleplayer Wordle game.")
            txt_file = open("combined_wordlist.txt", "r")
            wordlist = txt_file.read().split("\n")
            word_to_guess = random.choice(wordlist)
            print(word_to_guess)
            txt_file.close()
            embed = discord.Embed(title="Wordle!")
            embed.set_thumbnail(url="https://www.androidfreeware.net/img2/com-TechTreeGames-Wordle.jpg")
            embed.add_field(name="You have 6 tries to guess a 5 letter word!", value="The faster you guess it, the more you win. Good luck!")
            if cooldown < 10 or cooldown > 90:
                embed.set_footer(text="Since you set no guess time, it has been set to the default of 30 seconds.")
                cooldown = 30
            else:
                embed.set_footer(text=f"Guess time: {cooldown}.")
            await ctx.send(embed=embed)

            """

            every round occurs if it hasn't been 6 rounds yet, and all players haven't succeeded/left yet.
            a DM is sent to each player, with their previous guesses if it has passed round 1.
            then a reply from player DM channels is awaited; if valid (real 5 letter word + not previous guesses + player hasn't sent yet) the player's current_guess is set to that word.
            the player is added to the "sent" list. after __ seconds, any player not in the "sent" list is kicked out.
            each player's guess is passed to the round function and evaluated.

            I will leave a comment explaining the function of each block of code below. (so i dont forget)

            """

            tries = 1
            all_success = 0
            all_left = 0
            while tries <= 6 and not all_success and not all_left:
                sent = []
            
                #DMs each competitor to send their guess + sends their guess history, then waits for valid responses.
                for competitor in Competitor.all_competitors:
                    competitor.current_guess = ""
                    await competitor.user.create_dm()
                    embed = discord.Embed(title=f"Please send a valid guess. You have {cooldown} seconds.", description="Else, type **stop** to leave the game.")
                    string = ''
                    if len(competitor.guesses)>0 and multi:
                        string = ""
                        for guess in competitor.guess_history:
                            string += guess[0]+": "+guess[1]+'\n'
                        if not string: string = "Good luck!"
                        embed.add_field(name="Your previous guesses: \n", value=string)
                    if multi: 
                        await competitor.user.send(embed=embed)
                        await Competitor.check_for_reply(self, cooldown, word_to_guess, wordlist, sent) #Check from response from all competitors.
                    else:
                        def check(m):
                            if m.author==ctx.author and len(m.content)==5 and m.content.lower() not in competitor.guesses and m.content.lower() in wordlist: return 1
                            elif m.content.lower()=='stop': return 1
                            else: return 0
                        await ctx.send(embed=embed)
                        try:
                            reply = await self.bot.wait_for('message', timeout=cooldown, check=check)
                            Competitor.round(reply.content.lower(), word_to_guess, competitor)
                            sent.append(competitor.user)
                        except:
                            pass


                #Checks all competitors, leavers and winners and creates their embed fields; then, sends the embed in ctx channel.
                embed, all_success, left_string = await Wordle.gamestate_eval(self, sent, multi, all_success)

                if not Competitor.all_competitors and not all_success: #if all_competitors is empty ie no more players, end the game. No reward if game is prematurely completed.
                    msg = await ctx.send(embed=embed)
                    embed.add_field(name="It appears all players have not responded, or left.", value="Ending game...", inline=False) 
                    all_left = 1 
                    await msg.edit(embed=embed)    
                    break 

                elif left_string: #string to show who just left.
                    left_string[:-2]
                    embed.add_field(name="The following players didn't respond in time last round: ", value=left_string)
                
                embed.set_footer(text=f"Round {tries}/6")
                await ctx.send(embed=embed)
                tries+=1


            #reset round data of all players, append current round to round history, check if players are left or if ctx.author wants to continue game.
            current_players = ''
            for competitor in Competitor.all_competitors:
                competitor.previous_rounds.append(0)
                competitor.current_guess = ""
                competitor.guess_history = []
                competitor.guesses = []
                current_players += competitor.user.name+"\n"

            for competitor in Competitor.win:
                competitor.win = 0
                competitor.previous_rounds.append(len(competitor.guess_history))
                Competitor.all_competitors.append(competitor)
                Competitor.win.remove(competitor)
                competitor.current_guess = ""
                competitor.guess_history = []
                competitor.guesses = []
                current_players += competitor.user.name+"\n"

            for competitor in Competitor.left:
                competitor.previous_rounds.append(-1)

            if len(Competitor.all_competitors)==0:
                next_game=0
                continue

            def check(reaction, user):
                    if user==ctx.author:
                        return str(reaction.emoji) == "✔️" or str(reaction.emoji) == "❌"
                    return 0
            embed = discord.Embed(title=f"{ctx.author.name}, react ✔️ to start the next game, or ❌ to stop here.", description=f"Currently played: {rounds_played} rounds. Current players: \n{current_players}")
            msg = await ctx.send(embed=embed)
            await msg.add_reaction("✔️")
            await msg.add_reaction("❌")
            try:
                reaction, user = await self.bot.wait_for('reaction_add', timeout=15, check=check)
                if str(reaction.emoji) == "✔️":
                    embed = discord.Embed(title="Starting next game...")
                    await msg.edit(embed=embed)
                    rounds_played+=1
                    continue
                elif str(reaction.emoji) == "❌":
                    embed = discord.Embed(title="Ending game...")
                    await msg.edit(embed=embed)
                    next_game=0
                    continue
            except:
                await ctx.send(f"{ctx.author.name}, you ran out of time! Ending game.")
                next_game=0
                continue


        
            
        #end of game; set all users' active_game states to None and reset the user arrays.
        embed = discord.Embed(title="Wordle Game History", description=f"Rounds played: {rounds_played}")
        embed.set_thumbnail(url="https://www.androidfreeware.net/img2/com-TechTreeGames-Wordle.jpg") 
        Competitor.all_competitors += Competitor.left + Competitor.win
        for competitor in Competitor.all_competitors:
            sq.update_value(self.conn, bot_vars.main_table, "uid", competitor.user.id, "active_game", '')
            hist_string = ''
            for i in competitor.previous_rounds:
                if i==0: hist_string+="❌\n"
                elif i==-1: hist_string+="➖\n"
                else: 
                    if i==1: hist_string+=f"✔️ ({i} try)\n"
                    else: hist_string+=f"✔️ ({i} tries)\n"
            embed.add_field(name=competitor.user.name+":", value=hist_string, inline=True)
        await ctx.send(embed=embed)
        Competitor.all_competitors = []
        Competitor.left = []
        Competitor.win = []

            
            



                
