# -*- coding: utf-8 -*-
#  Copyright © 2020 StarrFox
#
#  ArcanumBot is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as published
#  by the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  ArcanumBot is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with ArcanumBot.  If not, see <https://www.gnu.org/licenses/>.

import random

import discord
from discord.ext import commands

url_base = 'https://cdn.discordapp.com/attachments/'
YODALINKS = [
    url_base + '480856274289033247/651635146189045787/mandalorian-baby-yoda-merch.jpg',
    url_base + '480856274289033247/651635159421943838/baby_yoda_song__1196588_1280x0.0.webp',
    url_base + '480856274289033247/651635166732746753/22dc4311a5b7c92d95d321a2f8f0a48bcf1dc00a.webp',
    url_base + '480856274289033247/651635173368004618/191129-baby-yoda-toys-christmas.webp',
    url_base + '480856274289033247/651635180687065090/Baby-Yoda-With-His-Little-Cup-Is-All-of-Us.jpg',
    url_base + '480856274289033247/651635187825770497/960x0.jpg',
    url_base + '480856274289033247/651635194087866388/109823337_960x0.jpg',
    url_base + '480856274289033247/651635224395907072/960x0-2.jpg',
]

class Fun(commands.Cog, name='fun'):

    @commands.command()
    async def yoda(self, ctx: commands.Context):
        """
        Sends a random baby yoda picture
        """
        embed = discord.Embed()
        embed.set_image(url=random.choice(YODALINKS))
        await ctx.send(embed=embed)


def setup(bot: commands.Bot):
    bot.add_cog(Fun(bot))
