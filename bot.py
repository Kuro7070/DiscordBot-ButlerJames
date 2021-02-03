import discord
from discord.ext import commands
from discord.ext.commands import CommandNotFound


description = '''An example bot to showcase the discord.ext.commands extension
module.
There are a number of utility commands being showcased here.'''

# this specifies what extensions to load when the bot starts up
startup_extensions = ['cogs.automatic', 'cogs.commanderrorhandler']

bot = commands.Bot(command_prefix='!', description=description)
bot.remove_command('help')


@bot.command(pass_context = True)
async def help(ctx):
    embed = discord.Embed(
        colour = discord.Colour.red()
    )
    author = ctx.message.author
    embed.set_author(name='Help')
    embed.add_field(name='Zusammenfassung', value='Der Bot merkt sich für jeden Channel jeweils alle hinzugefügten Subreddits und postet im angegebenen Intervalle immer aus einem der Subreddits(der Subreddit wird zufällig ausgesucht) einen zufälligen Post', inline=False)
    embed.add_field(name='!add subreddit', value='Fügt einen Subreddit dem aktuellen Channel hinzu', inline=False)
    embed.add_field(name='!remove subreddit', value='Entfernt einen Subreddit aus dem aktuellen Channel', inline=False)
    embed.add_field(name='!help', value='Zeigt alle möglichen Commands an', inline=False)
    embed.add_field(name='!active', value='Zeigt die aktiven Subreddits der Channels an', inline=False)
    embed.add_field(name='!repeat_time Zeit in Sekunden', value='Ändert die zeitliche Wiederholrate des postings. In Sekunden!!!!', inline=False)

    try:
        await ctx.channel.send(author, embed=embed)
    except (commands.HTTPException, commands.Forbidden, commands.InvalidArgument) as error:
        print('Nachricht konnte nicht gesendet werden')
        traceback.print_exc()


@bot.command()
async def load(ctx, message):
    """Load an extension."""
    if not isPrivateChat(ctx.channel):
        try:
            bot.load_extension('cogs.' + message)
            await ctx.send('Programm: ' + message + ' wurde aktiviert')
        except discord.ext.commands.ExtensionNotLoaded as error:
            await ctx.send('Programm wurde nicht gefunden oder existiert nicht')
            return

@load.error
async def load_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('Die Parametereingabe war falsch')
        return
    else:
        print('Load Command -> es gab einen Fehler und er wurde ignoriert')
        return





@bot.command()
async def unload(ctx, message):
    """Unloads an extension."""
    
    if not isPrivateChat(ctx.channel):
        try:
            bot.unload_extension('cogs.' + message)
            await ctx.send('Programm: ' + message + ' wurde deaktiviert')
        except discord.ext.commands.ExtensionNotLoaded as error:
            await ctx.send('Programm existiert nicht oder ist bereits deaktiviert')
            return

@unload.error
async def unload_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('Die Parametereingabe war falsch')
        return
    else:
        print('Unload Command -> es gab einen Fehler und er wurde ignoriert')
        return



def isPrivateChat(channel):
    return isinstance(channel, discord.channel.DMChannel)

async def send_message(channel, message):
    try:
        await channel.send(message)
    except (commands.HTTPException, commands.Forbidden, commands.InvalidArgument) as error:
        print('Nachricht konnte nicht gesendet werden')
        traceback.print_exc()



if __name__ == "__main__":
    for extension in startup_extensions:
        try:
            bot.load_extension(extension)
        except discord.ext.commands.ExtensionNotLoaded as error:
            exc = '{}: {}'.format(type(e).__name__, e)
            print("\n\n")
            print('Failed to load extension {extension}')
            print("\n\n")
            traceback.print_exc()
            print("\n\n")

    bot.run(token)
