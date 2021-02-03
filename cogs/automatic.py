import discord
from discord.ext import tasks, commands
import asyncio
import praw
import json
import prawcore
from praw.exceptions import APIException
import copy
import random
import os.path
import errno
from pathlib import Path
from datetime import datetime
import pytz

class Automatic(commands.Cog):
    
    
    def __init__(self, bot):
        self.bot = bot
        self.current_path  = os.path.dirname(os.path.realpath(__file__))
        self.subdir = "cog_configs"
        self.automatic_config = "automatic_config.json"
        self.automatic_cfg_path = os.path.join(self.current_path, self.subdir, self.automatic_config)


        self.reddit = praw.Reddit(client_id='ztWL03UO7h5Qmw',
                client_secret='ItRYl1ewZM0N2KGX3SCAvqtf2Ifxeg',
                user_agent='DiscordBot')

        try:
            os.mkdir(os.path.join(self.current_path, self.subdir))
        except OSError as exc:
            if exc.errno != errno.EEXIST:
                traceback.print_exc()
            pass

        self.data_set = "{}"
        self.reddit_list = {}  
        self.parent_path = Path(self.current_path).parent
        self.loadTime()
        self.loadConfig()

        #Print der Startparameter
        print("Liste mit den Einträgen der Subreddits: " + str(self.reddit_list))
        print("Parameter für die Wiederholung der postings: " + str(self.loop_para))
    
    #Variables
    loop_para = 600

    def loadConfig(self):

        try:
            config = open(self.automatic_cfg_path)
            data = json.load(config)
            self.reddit_list = data
        except IOError:
            print("Config File ist nicht existent \nConfigFile wird nun erzeugt")
            config = open(self.automatic_cfg_path, "x")
            config.write(self.data_set)
        finally:
            config.close()



    def loadTime(self):
        global loop_para
        gen_config = str(self.parent_path) +'\gen_config.json'
        backup_para = self.loop_para
        try:
            config = open(gen_config)
            data = json.load(config)
            loop_para = data.get("automatic_loop_para")

        except IOError:
            print("Allgemeine Config File ist nicht existent \nConfigFile wird nun erzeugt")
            config = open(gen_config, "x")
            #general_dict = "{\"automatic_loop_para\":\"" + str(self.loop_para) + "\"}"
            general_dict = {"automatic_loop_para": backup_para}
            json_object = json.dumps(general_dict, indent = 4)   

            config.write(json_object)
        finally:
            config.close()


    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.loop.create_task(self.auto_meme())



    #@tasks.loop(seconds=loop_para)
    async def auto_meme(self):
        while not self.bot.is_closed():              
            tz = pytz.timezone('Europe/Berlin')
            current_time = datetime.now(tz).hour
            if (current_time > 10 and current_time < 24) or (current_time > 0 and current_time < 3):
                
                try:
                    for channel_id in self.reddit_list.keys():

                        random_subreddit = random.choice(self.reddit_list.get(channel_id))

                        subreddit = self.reddit.subreddit(random_subreddit) 
                        meme = subreddit.random()
                        if subreddit is not None and meme is not None:
                            finished_message = "Subreddit: " + str(subreddit) + "\n" + meme.url
                            await self.send_message(self.bot.get_channel(int(channel_id)), finished_message)
                            

                        elif meme is None:

                            meme_list = []
                            for submission in self.reddit.subreddit(random_subreddit).hot(limit=200):
                                meme_list.append(submission)

                            random_meme = random.choice(meme_list)

                            finished_message = "Subreddit: " + str(subreddit) + "\n" + random_meme.url
                            await self.send_message(self.bot.get_channel(int(channel_id)), finished_message)
                            
                except:
                    for channel_id in self.reddit_list.keys():
                        finished_message ='Es gab einen Fehler bei posten der Memes, bitte Entschuldigen Sie uns Meister'
                        await self.send_message(self.bot.get_channel(int(channel_id)),finished_message)
                        traceback.print_exc()
            
            await asyncio.sleep(self.loop_para)








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
                    finished_message = "Dieser Subreddit ist entweder privat oder nicht existent"
                    await self.send_message(ctx.channel, finished_message)
                    

            else:
                finished_message = "Die Eingabe war falsch. Beispiel: !add Subreddit_Name"
                await self.send_message(ctx.channel, finished_message)

    @add.error
    async def add_error(ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('Die Parametereingabe war falsch')
            return
        else:
            print('Add Command -> es gab einen Fehler und er wurde ignoriert')
            return



    @commands.command()
    async def remove(self, ctx):

        if not self.isPrivateChat(ctx.channel):
            channel_id = ctx.message.channel.id
            message_split = ctx.message.content.split(' ')

            if len(message_split) == 2:
                subreddit = message_split[1]
                if str(channel_id) in self.reddit_list and str(subreddit) in self.reddit_list.get(str(channel_id)):
                    await self.remove_subreddit(subreddit, channel_id)
                else:
                    finished_message = "Dieser Subreddit ist nicht aktiv"
                    await self.send_message(ctx.channel, finished_message)


            else:
                finished_message = "Die Eingabe war falsch. Beispiel: !remove Subreddit_Name"
                await self.send_message(ctx.channel, finished_message)

    @remove.error
    async def remove_error(ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('Die Parametereingabe war falsch')
            return
        else:
            print('Remove Command -> es gab einen Fehler und er wurde ignoriert')
            return 


    @commands.command(pass_context = True)
    async def active(self, ctx):

        if not self.isPrivateChat(ctx.channel):
            server_id = ctx.guild.id
            dict_data = {}
            for channel in self.reddit_list.keys():
                
                if server_id == self.bot.get_channel(int(channel)).guild.id:
                    #key = channel_id
                    #val = subreddit liste
                    channel_name = self.bot.get_channel(int(channel)).name
                    templiste = []
                    for subreddit in self.reddit_list.get(str(channel)):
                        templiste.append(subreddit)
                    dict_data[channel_name] = templiste

            if len(dict_data.keys()) > 0:
               
                embed = discord.Embed(
                colour = discord.Colour.red()
                )
                author = ""
                embed.set_author(name='Active')
                for key in dict_data:
                    print_list = '   '.join(dict_data.get(key))
                    embed.add_field(name=('Channel: ' + str(key)), value=print_list, inline=False)

                try:
                    await ctx.channel.send(author, embed=embed)
                except (commands.HTTPException, commands.Forbidden, commands.InvalidArgument) as error:
                    print('Nachricht konnte nicht gesendet werden')
                    traceback.print_exc()

            else:
                finished_message = "\nZur zeit sind keine Subreddits aktiv\n"
                await self.send_message(ctx.channel, finished_message)

    @active.error
    async def active_error(ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('Die Parametereingabe war falsch')
            return
        else:
            print('Active Command -> es gab einen Fehler und er wurde ignoriert')
            return 



    @commands.command()
    async def repeat_time(self, ctx):
        global loop_para
        if not self.isPrivateChat(ctx.channel):
            repeat_number = ctx.message.content.split(' ')
            if len(repeat_number)== 2:
                repeat_number = repeat_number[1]
                backup_loop_para = self.loop_para
                if repeat_number.isnumeric():
                    repeat_number = int(repeat_number)
                    if repeat_number > 600:
                        self.loop_para = repeat_number
                        gen_config = str(self.parent_path) +'\gen_config.json'

                        try:
                            config = open(gen_config)
                            data = json.load(config)
                            data["automatic_loop_para"] = self.loop_para

                            with open(gen_config, 'w') as json_file_write:
                                json.dump(data, json_file_write,  indent = 4)


                        except IOError:
                            print("Fehler beim überschreiben der Allgemeinen Config Datei")
                            loop_para = backup_loop_para
                        finally:
                            config.close()
                            json_file_write.close()


                        await self.send_message(ctx.channel, "Der Wiederholzeitraum für das senden von Memes wurde auf: " + str(self.loop_para) + " aktualisiert")

                    else:
                        await self.send_message(ctx.channel, "Der Parameter war zu klein. Er muss mindestens 600 Sekunden betragen")
                else:
                    await self.send_message(ctx.channel, "Der Parameter war kein gültiger Wert")
            else:
                await self.send_message(ctx.channel, "Es wurde kein Parameter übergeben")

    @repeat_time.error
    async def repeat_time_error(ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('Die Parametereingabe war falsch')
            return
        else:
            print('Load Command -> es gab einen Fehler und er wurde ignoriert')
            return



        
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

        channel_id = ctx.message.channel.id
        message_split = ctx.message.content.split(' ')
        subreddit = message_split[1]
        
        if str(channel_id) in self.reddit_list.keys():

            if str(subreddit) in self.reddit_list.get(str(channel_id)):
                # subreddit und channel enthalten -> rauspringen

                finished_message = "Dieser Subreddit ist für diesen Channel bereits aktiv"
                await self.send_message(ctx.channel, finished_message)

                return False
            else:
                # channel enthalten, subreddit aber nicht -> channel hinzufügen
                backup_reddit_list = copy.deepcopy(self.reddit_list)
                try:                        
                    self.reddit_list.get(str(channel_id)).append(subreddit)

                    with open(self.automatic_cfg_path, 'w') as json_file_write:
                        json.dump(self.reddit_list, json_file_write,  indent = 4)
                except IOError as e:
                    self.reddit_list = backup_reddit_list

                    finished_message = "Es gab einen Fehler beim hinzufügen des Channels"
                    await self.send_message(ctx.channel, finished_message)
                    return False
                finally:
                    json_file_write.close()
        else:
            # channel nicht enthalten und subreddit auch nicht
                backup_reddit_list = copy.deepcopy(self.reddit_list)
                try:
                    self.reddit_list[str(channel_id)] = [subreddit]

                    with open(self.automatic_cfg_path, 'w') as json_file_write:
                        json.dump(self.reddit_list, json_file_write,  indent = 4)

                except IOError as e:
                    self.reddit_list = backup_reddit_list
                    
                    
                    finished_message = "Es gab einen Fehler beim hinzufügen des Subreddits und des Channels"
                    await self.send_message(ctx.channel, finished_message)
                    return False
                finally:
                    json_file_write.close()
    

        finished_message = "Der Subreddit wurde erfolgreich hinzugefügt"
        await self.send_message(ctx.channel, finished_message)
        return True


    async def remove_subreddit(self, subreddit, channel_id):


        # channel enthalten, subreddit aber nicht -> channel hinzufügen
        backup_reddit_list = copy.deepcopy(self.reddit_list)
        try:                        
            self.reddit_list.get(str(channel_id)).remove(subreddit)

            if len(self.reddit_list.get(str(channel_id))) == 0:
                del self.reddit_list[str(channel_id)]

            with open(self.automatic_cfg_path, 'w') as json_file_write:
                json.dump(self.reddit_list, json_file_write,  indent = 4)
        except IOError as e:
            self.reddit_list = backup_reddit_list

            finished_message = "Es gab einen Fehler beim entfernen des Subreddits"
            await self.send_message(self.bot.get_channel(channel_id).channel, finished_message)
            return False
        finally:
            json_file_write.close()
    
    
        finished_message = "Der Subreddit wurde erfolgreich entfernt"
        await self.send_message(self.bot.get_channel(channel_id), finished_message)
        return True

    async def send_message(self, channel, message):
        try:
            await channel.send(message)
        except (commands.HTTPException, commands.Forbidden, commands.InvalidArgument) as error:
            print('Nachricht konnte nicht gesendet werden')
            traceback.print_exc()

def setup(bot):
    bot.add_cog(Automatic(bot))
    print('Automatic-Program is loaded')











