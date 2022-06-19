import os

import discord
from discord.ext import commands

from commands.main_commands import MainCommands
from commands.music_commands import MusicCommands
from commands.playlist_commands import PlaylistCommands
from commands.rng_commands import RngCommands
from commands.text_commands import TextCommands

bot = commands.Bot(command_prefix='/')

@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))
    await bot.change_presence(activity=discord.Game('/commands'))

bot.add_cog(MainCommands(bot))
bot.add_cog(MusicCommands(bot))
bot.add_cog(PlaylistCommands(bot))
bot.add_cog(RngCommands(bot))
bot.add_cog(TextCommands(bot))

bot.run(os.environ['TOKEN'])