import random

from discord.ext import commands

class RngCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.setup()

    def setup(self):
        print('Rng commands loaded')

    def isnumber(self, x):
        if x.isnumeric():
            return True
        
        if x.startswith('-') and x[1:].isnumeric():
            return True

        return False

    @commands.command(aliases=['mince', 'coin'])
    async def _coin(self, ctx):
        res = random.randint(0, 1)
        await ctx.send(f':pizza: <@{ctx.author.id}> hodil {"pannu" if res == 0 else "orel"}')

    @commands.command(aliases=['rng'])
    async def _rng(self, ctx, *args):
        if not len(args) == 2:
            await ctx.send(f':pizza: <@{ctx.author.id}>, zadej dvě čísla')
            return

        if not self.isnumber(args[0]) or not self.isnumber(args[1]):
            await ctx.send(f':pizza: <@{ctx.author.id}>, to nejsou čísla')
            return

        low = min(args)
        high = max(args)
        rng = random.randint(int(low), int(high))
        await ctx.send(f':pizza: <@{ctx.author.id}>, bylo zvoleno {rng}')