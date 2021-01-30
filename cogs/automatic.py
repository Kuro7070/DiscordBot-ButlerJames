import discord
from discord.ext import tasks, commands
import asyncio
import praw
import json
import prawcore
from praw.exceptions import APIException
import copy
import random

class Automatic(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot
        self.loadConfig()
            

 

    ### Variables ###
    reddit_list = {}  

    ##Aufbau
    #{
    # server: {channel = ([subreddits]), channel = ([subreddits])},
    # server: {channel = ([subreddits]), channel = ([subreddits])}
    # }

    def loadConfig(self):
        global data_set, reddit_list
        try:
            config = open("config.json")
            data = json.load(config)
            reddit_list = data
            print(reddit_list)
        except IOError:
            print("Config File ist nicht existent \nConfigFile wird nun erzeugt")
            config = open("config.json", "x")
            config.write(data_set)
        finally:
            config.close()


    @commands.Cog.listener()
    async def on_ready(self):
        self.auto_meme.start()


    @tasks.loop(seconds=20)
    async def auto_meme(self):
        global reddit_list

                       
        reddit = praw.Reddit(client_id='ztWL03UO7h5Qmw',
                        client_secret='ItRYl1ewZM0N2KGX3SCAvqtf2Ifxeg',
                        user_agent='DiscordBot')

        
        try:
            for channel_id in reddit_list.keys():

                random_subreddit = random.choice(reddit_list.get(channel_id))

                subreddit = reddit.subreddit(random_subreddit) 
                meme = subreddit.random()
                if subreddit is not None and meme is not None:
                    print(channel_id)
                    await self.bot.get_channel(int(channel_id)).send("Subreddit: " + self.bot.get_channel(int(channel_id)).name + "\n" + meme.url)

                elif meme is None:

                    meme_list = []
                    for submission in reddit.subreddit(random_subreddit).hot(limit=200):
                        meme_list.append(submission)

                    random_meme = random.choice(meme_list)

                    await self.bot.get_channel(int(channel_id)).send("Subreddit: " + self.bot.get_channel(int(channel_id)).name + "\n" + random_meme.url)
                    
        except:
            for channel_id in reddit_list.keys():
                await self.bot.get_channel(int(channel_id)).send('Es gab einen Fehler bei posten der Memes, bitte Entschuldigen Sie uns Meister')
    








### Chat Commands ###
    @commands.command()
    async def add(self, ctx):
        if not self.isPrivateChat(ctx.channel):
            server_name = ctx.guild.name
            channel_id = ctx.message.channel.id
            message_split = ctx.message.content.split(' ')

            if len(message_split) == 2:
                subreddit = message_split[1]
                if self.sub_exists(subreddit):
                    await self.add_subreddit(ctx)
                else:
                    await message.channel.send(
                    "Dieser Subreddit ist entweder privat oder nicht existent")

            else:
                await message.channel.send(
                "Die Eingabe war falsch. Beispiel: !add Subreddit_Name")


    @commands.command()
    async def remove(self, ctx):
        global reddit_list
        if not self.isPrivateChat(ctx.channel):
            channel_id = ctx.message.channel.id
            message_split = ctx.message.content.split(' ')

            if len(message_split) == 2:
                subreddit = message_split[1]
                if str(channel_id) in reddit_list and str(subreddit) in reddit_list.get(str(channel_id)):
                    await self.remove_subreddit(subreddit, channel_id)
                else:
                    #await message.channel.send(
                    print("Dieser Subreddit ist nicht aktiv")

            else:
                # await message.channel.send(
                print("Die Eingabe war falsch. Beispiel: !remove Subreddit_Name")


    @commands.command()
    async def active(self, ctx):
        global reddit_list
        if not self.isPrivateChat(ctx.channel):
            server_id = ctx.guild.id
            dict_data = {}
            for channel in reddit_list.keys():
                
                if server_id == self.bot.get_channel(int(channel)).guild.id:
                    #key = channel_id
                    #val = subreddit liste
                    channel_name = self.bot.get_channel(int(channel)).name
                    templiste = []
                    for subreddit in reddit_list.get(str(channel)):
                        templiste.append(subreddit)
                    dict_data[channel_name] = templiste

            if len(dict_data.keys()) > 0:
                print_dic = ""
                for key, value in dict_data.items():
                    print_dic += (key + " : " + ', '.join(value) + "\n")

                await ctx.channel.send("\nZur Zeit sind folgende Subreddits aktiv:\n" + print_dic + "\n")
            else:
                await ctx.channel.send("\nZur zeit sind keine Subreddits aktiv\n")









        
    ### normale Methoden ###

    def isPrivateChat(self,channel):
        return isinstance(channel, discord.channel.DMChannel)



    def sub_exists(self,sub):
                    
        reddit = praw.Reddit(client_id='ztWL03UO7h5Qmw',
                        client_secret='ItRYl1ewZM0N2KGX3SCAvqtf2Ifxeg',
                        user_agent='DiscordBot')
                        
        try:
            reddit.subreddits.search_by_name(sub, exact=True)
        except prawcore.exceptions.NotFound:
            return False

        try:
            if reddit.subreddit(sub).subreddit_type != 'public':
                return False
        except:
            return False

        return True


    async def add_subreddit(self, ctx):
        global reddit_list
        channel_id = ctx.message.channel.id
        message_split = ctx.message.content.split(' ')
        subreddit = message_split[1]
        
        if str(channel_id) in reddit_list.keys():

            if str(subreddit) in reddit_list.get(str(channel_id)):
                # subreddit und channel enthalten -> rauspringen
                #await bot.get_channel(channel_id).send(
                await ctx.channel.send("Dieser Subreddit ist für diesen Channel bereits aktiv")
                return False
            else:
                # channel enthalten, subreddit aber nicht -> channel hinzufügen
                backup_reddit_list = copy.deepcopy(reddit_list)
                try:                        
                    reddit_list.get(str(channel_id)).append(subreddit)

                    with open('config.json', 'w') as json_file_write:
                        json.dump(reddit_list, json_file_write)
                except IOError as e:
                    reddit_list = backup_reddit_list
                    await ctx.channel.send('Es gab einen Fehler beim hinzufügen des Channels')
                    return False
                finally:
                    json_file_write.close()
        else:
            # channel nicht enthalten und subreddit auch nicht
                backup_reddit_list = copy.deepcopy(reddit_list)
                try:
                    reddit_list[str(channel_id)] = [subreddit]

                    with open('config.json', 'w') as json_file_write:
                        json.dump(reddit_list, json_file_write)

                except IOError as e:
                    reddit_list = backup_reddit_list
                    
                    await ctx.channel.send('Es gab einen Fehler beim hinzufügen des Subreddits und des Channels')
                    return False
                finally:
                    json_file_write.close()
    
        await ctx.channel.send("Der Subreddit wurde erfolgreich hinzugefügt")
        return True


    async def remove_subreddit(self, subreddit, channel_id):
        global reddit_list


        # channel enthalten, subreddit aber nicht -> channel hinzufügen
        backup_reddit_list = copy.deepcopy(reddit_list)
        try:                        
            reddit_list.get(str(channel_id)).remove(subreddit)

            if len(reddit_list.get(str(channel_id))) == 0:
                del reddit_list[str(channel_id)]

            with open('config.json', 'w') as json_file_write:
                json.dump(reddit_list, json_file_write)
        except IOError as e:
            reddit_list = backup_reddit_list
            await ctx.channel.send('Es gab einen Fehler beim entfernen des Subreddits')
            return False
        finally:
            json_file_write.close()
    
    
    

        print(reddit_list)
        await ctx.channel.send('Der Subreddit wurde erfolgreich entfernt')
        return True



def setup(bot):
    bot.add_cog(Automatic(bot))
    print('Automatic-Program is loaded')











