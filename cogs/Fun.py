import random
import discord

from discord.ext import commands

yodalinks = None
with open('yodalinks.txt') as fp:
    yodalinks = fp.readlines()

class fun(commands.Cog):

    @commands.command()
    async def yoda(self, ctx: commands.Context):
        """
        Sends a random baby yoda picture
        """
        pick = random.choice(yodalinks)
        embed = discord.Embed()
        embed.set_image(url=pick)
        await ctx.send(embed=embed)

def setup(bot: commands.Bot):
    bot.add_cog(fun())
