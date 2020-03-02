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

import discord
import logging

from discord.ext import commands
from discord_chan import NormalPageSource, DCMenuPages

from arcanumbot import checks, EmojiGameMenu, ArcanumBot

logger = logging.getLogger(__name__)

class aacoins(commands.Cog):

    def __init__(self, bot: ArcanumBot):
        self.bot = bot

    @commands.group(name='coins', invoke_without_command=True)
    async def view_aacoins(self, ctx: commands.Context, member: discord.Member = None):
        """
        View another member or your aacoin amount
        """
        member = member or ctx.author
        amount = await self.bot.get_aacoin_amount(member.id)
        await ctx.send(f"{member} has {amount} aacoin(s).")

    @view_aacoins.command(name='all')
    async def view_all_aacoins(self, ctx: commands.Context):
        """
        View all aacoins sorted by amount
        """
        lb = await self.bot.get_aacoin_lb()

        entries = []
        for user_id, coins in lb:
            member = self.bot.guild.get_member(user_id)
            entries.append(f'{member}: {coins}')

        source = NormalPageSource(entries, per_page=10)

        menu = DCMenuPages(source)

        await menu.start(ctx)

    @commands.command(name='add')
    @checks.is_coin_mod_or_above()
    async def add_aacoins(self, ctx: commands.Context, member: discord.Member, amount: int):
        """
        Add aacoins to a member
        """
        current = await self.bot.get_aacoin_amount(member.id)
        await self.bot.set_aacoins(member.id, current + amount)
        message = f"Added {amount} to {member}'s aacoin(s)."
        await ctx.send(message)

    @commands.command(name='remove')
    @checks.is_coin_mod_or_above()
    async def remove_aacoins(self, ctx: commands.Context, member: discord.Member, amount: int):
        """
        Remove aacoins from a member
        """
        current = await self.bot.get_aacoin_amount(member.id)
        await self.bot.set_aacoins(member.id, current - amount)
        message = f"Removed {amount} from {member}'s aacoin(s)."
        await ctx.send(message)

    @commands.command(name='clear')
    @checks.is_coin_mod_or_above()
    async def clear_aacoins(self, ctx: commands.Context, member: discord.Member):
        """
        Clear a member's aacoin(s)
        """
        await self.bot.delete_user_aacoins(member.id)
        message = f"Cleared {member}'s aacoin(s)."
        await ctx.send(message)

    @commands.command(name='react')
    async def aacoins_react_game(self, ctx: commands.Context):
        """
        Play a game of Emoji react
        """
        game = EmojiGameMenu()
        value = await game.run(ctx)

        if value:
            current = await self.bot.get_aacoin_amount(ctx.author.id)
            await self.bot.set_aacoins(ctx.author.id, current + value)

            await ctx.send(f'\N{PARTY POPPER} you won {value} {ctx.bot.aacoin}s\n'
                           f'you now have a total of {await self.bot.get_aacoin_amount(ctx.author.id)}')

        else:
            await ctx.send(f'React timed out.')

def setup(bot: ArcanumBot):
    bot.add_cog(aacoins(bot))
