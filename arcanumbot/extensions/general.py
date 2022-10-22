import random

import discord
from discord.ext import commands

url_base = "https://cdn.discordapp.com/attachments/"
YODALINKS = [
    url_base + "480856274289033247/651635146189045787/mandalorian-baby-yoda-merch.jpg",
    url_base
    + "480856274289033247/651635159421943838/baby_yoda_song__1196588_1280x0.0.webp",
    url_base
    + "480856274289033247/651635166732746753/22dc4311a5b7c92d95d321a2f8f0a48bcf1dc00a.webp",
    url_base
    + "480856274289033247/651635173368004618/191129-baby-yoda-toys-christmas.webp",
    url_base
    + "480856274289033247/651635180687065090/Baby-Yoda-With-His-Little-Cup-Is-All-of-Us.jpg",
    url_base + "480856274289033247/651635187825770497/960x0.jpg",
    url_base + "480856274289033247/651635194087866388/109823337_960x0.jpg",
    url_base + "480856274289033247/651635224395907072/960x0-2.jpg",
]


class General(commands.Cog, name="general"):
    @commands.command()
    async def yoda(self, ctx: commands.Context):
        """
        Sends a random baby yoda picture
        """
        embed = discord.Embed()
        embed.set_image(url=random.choice(YODALINKS))
        await ctx.send(embed=embed)

    @commands.command()
    async def ping(self, ctx: commands.Context):
        """
        Sends the bot's websocket latency
        """
        await ctx.send(
            f"\N{TABLE TENNIS PADDLE AND BALL} {round(ctx.bot.latency * 1000)}ms"
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(General(bot))
