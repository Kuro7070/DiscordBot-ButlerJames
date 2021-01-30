import discord
from discord.ext import commands


description = '''An example bot to showcase the discord.ext.commands extension
module.
There are a number of utility commands being showcased here.'''

# this specifies what extensions to load when the bot starts up
startup_extensions = ['cogs.automatic']

bot = commands.Bot(command_prefix='!', description=description)


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



def isPrivateChat(self, channel):
    return isinstance(channel, discord.channel.DMChannel)




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