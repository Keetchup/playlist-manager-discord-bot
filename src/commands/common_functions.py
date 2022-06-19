import discord
import asyncio

class MultiPagePrinter():
    def __init__(self, bot, ctx, items, title, items_per_page):
        self.bot = bot
        self.ctx = ctx
        self.items = items
        self.title = title
        self.items_per_page = items_per_page

    def current_page_print(self, cur_page, pages):
        embed = discord.Embed(title=f':pizza: {self.title}', description="", colour=discord.Colour.dark_gold())
        max = self.items_per_page if cur_page * self.items_per_page <= len(self.items) else len(self.items) % self.items_per_page

        for i in range (0, max):
            embed.description += f"{(cur_page - 1) * self.items_per_page + i + 1}) {self.items[(cur_page - 1) * self.items_per_page + i]}\n"

        embed.set_footer(text=f"Page {cur_page}/{pages}\n")
        return embed

    async def print(self):
        pages = (len(self.items) + self.items_per_page - 1) // self.items_per_page
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