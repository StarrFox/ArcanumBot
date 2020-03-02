# -*- coding: utf-8 -*-
#  Copyright © 2020 StarrFox
#
#  Discord Chan is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as published
#  by the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  Discord Chan is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with Discord Chan.  If not, see <https://www.gnu.org/licenses/>.

from dataclasses import dataclass

import discord
from discord.ext import menus, commands


# This is super bad but /shrug
@dataclass()
class MockContext:
    bot: commands.bot
    author: discord.User
    guild: discord.Guild
    channel: discord.TextChannel

class ConfirmDeleteMenu(menus.Menu):

    def __init__(self, user_id, **kwargs):
        super().__init__(
            timeout=kwargs.pop('timeout', None),
            **kwargs
        )
        self.user_id = user_id
        self.response = None

    async def send_initial_message(self, ctx, channel):
        starrfox = ctx.bot.guild.get_member(285148358815776768)

        try:
            user = await self.bot.fetch_user(self.user_id)
        except discord.NotFound:
            user = '[Deleted]'

        return await ctx.bot.logging_channel.send(
            f'{starrfox.mention} Userid {self.user_id} was not found in guild.\n'
            f'id resolves to {user}\n'
            f'discard?'
        )

    @menus.button('\N{WHITE HEAVY CHECK MARK}')
    async def do_yes(self, _):
        self.response = True
        self.stop()

    @menus.button('\N{CROSS MARK}')
    async def do_no(self, _):
        self.response = False
        self.stop()

    async def get_response(self, ctx):
        await self.start(ctx, wait=True)
        return self.response

