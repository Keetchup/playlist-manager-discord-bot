import random
import discord

from discord.ext import commands

class TextCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.setup()

    def setup(self):
        print('Text commands loaded')

    @commands.command(aliases=['delka'])
    async def _dong_1(self, ctx):
        length = random.randint(0, 35)
        await ctx.send(f':pizza: <@{ctx.author.id}> ho má {str(length)} centimetrů dlouhého :smiling_imp::eggplant:')

    @commands.command(aliases=['sirka'])
    async def _dong_2(self, ctx):
        length = random.randint(0, 10)
        await ctx.send(f':pizza: <@{ctx.author.id}> ho má {str(length)} centimetrů širokého :smiling_imp::eggplant:')
        
    @commands.command(aliases=['lockdown'])
    async def _lockdown_(self, ctx):
        title = ':pizza: Lockdown'
        url = 'https://www.youtube.com/watch?v=4BH9iSt8Vy0'
        description = 'i když :broken_heart: jsi :crying_cat_face: ode mne tisíce :100: 0 mil, nedovolím :angry: aby nás lockdown :closed_lock_with_key: rozdělil :sweat_drops: nikdo není tak silnej :muscle: aby naší lásku :heart: ️ jen tak zabil :x:'
        await ctx.send(embed=discord.Embed(title=title, url=url, description=description, colour=discord.Colour.dark_gold()))