import discord
import asyncio

from discord.ext import commands

class MainCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.command_list = []
        self.setup()

    def setup(self):
        self.add_main_commands()
        self.add_music_commands()
        self.add_playlist_commands()
        self.add_text_commands()
        self.add_rng_commands()
        print('Main commands loaded')

    def add_main_commands(self):
        main = []
        main.append('__**Main**__')
        main.append('/**commands** - lists all commands in pager')
        self.command_list.append(main)

    def add_music_commands(self):
        music = []
        music.append('__**Music**__')
        music.append('/**join** - music bot connects to voice channel')
        music.append('/**leave** - music bot leaves voice channel')
        music.append('/**quickplay** | **qp** - plays quick playlist')
        music.append('/**queue list** - lists songs in queue')
        music.append('/**queue add** [youtube-url] - adds song to the queue')
        music.append('/**queue current** - returns currently playing song')
        music.append('/**play** - starts playing songs in queue')
        music.append('/**stop** - stops playing')
        music.append('/**pause** - pauses current track')
        music.append('/**resume** - resumes current track')
        music.append('/**next** - skips to next song')
        music.append('/**loop** - toggles loop setting')
        music.append('/**clear** - empties song queue')
        self.command_list.append(music)

    def add_playlist_commands(self):
        playlist = []
        playlist.append('__**Playlist**__')
        playlist.append('/**playlist add** [youtube-url] - adds song to the quick playlist')
        playlist.append('/**playlist list** - lists songs in playlist')
        self.command_list.append(playlist)

    def add_text_commands(self):
        text = []
        text.append('__**Text**__')
        text.append('/**delka**')
        text.append('/**sirka**')
        text.append('/**lockdown** - copypasta')
        
        self.command_list.append(text)

    def add_rng_commands(self):
        rng = []
        rng.append('__**RNG**__')
        rng.append('/**coin** - toss a coin')
        rng.append('/**rng** [x1] [x2] - randomly selects number between x1 and x2')
    
    @commands.command(aliases=['commands'])
    async def _help(self, ctx):
        printer = CommandsPrinter(self.bot, ctx, self.command_list)
        await printer.print()

class CommandsPrinter():
    def __init__(self, bot, ctx, items):
        self.bot = bot
        self.ctx = ctx
        self.items = items

    def current_page_print(self, cur_page, pages):
        embed = discord.Embed(title='Commands', description="", colour=discord.Colour.dark_gold())

        for item in self.items[cur_page - 1]:
            embed.description += f"{item}\n"

        embed.set_footer(text=f"Page {cur_page}/{pages}\n")
        return embed

    async def print(self):
        pages = len(self.items)
        cur_page = 1

        message = await self.ctx.send(embed=self.current_page_print(cur_page, pages))

        await message.add_reaction("◀️")
        await message.add_reaction("▶️")

        def check(reaction, user):
            return user == self.ctx.author and str(reaction.emoji) in ["◀️", "▶️"]

        while True:
            try:
                reaction, user = await self.bot.wait_for("reaction_add", timeout=60, check=check)

                if str(reaction.emoji) == "▶️" and cur_page != pages:
                    cur_page += 1
                    await message.edit(embed=self.current_page_print(cur_page, pages))
                    await message.remove_reaction(reaction, user)

                elif str(reaction.emoji) == "◀️" and cur_page > 1:
                    cur_page -= 1
                    await message.edit(embed=self.current_page_print(cur_page, pages))
                    await message.remove_reaction(reaction, user)

                else:
                    await message.remove_reaction(reaction, user)
            except asyncio.TimeoutError:
                await message.clear_reactions()
                break