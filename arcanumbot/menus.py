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

from dataclasses import dataclass
from typing import Sequence

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
        super().__init__(timeout=kwargs.pop("timeout", None), **kwargs)
        self.user_id = user_id
        self.response = None

    async def send_initial_message(self, ctx, channel):
        starrfox = ctx.bot.guild.fetch_member(285148358815776768)

        try:
            user = await self.bot.fetch_user(self.user_id)
        except discord.NotFound:
            user = "[Deleted]"

        return await ctx.bot.logging_channel.send(
            f"{starrfox.mention} Userid {self.user_id} was not found in guild.\n"
            f"id resolves to {user}\n"
            f"discard?"
        )

    @menus.button("\N{WHITE HEAVY CHECK MARK}")
    async def do_yes(self, _):
        self.response = True
        self.stop()

    @menus.button("\N{CROSS MARK}")
    async def do_no(self, _):
        self.response = False
        self.stop()

    async def get_response(self, ctx):
        await self.start(ctx, wait=True)
        return self.response


class MenuPages(menus.MenuPages):
    def __init__(self, source, **kwargs):
        super().__init__(source, **kwargs)

    def skip_two_or_less(self):
        max_pages = self._source.get_max_pages()
        if max_pages is None:
            return True
        return max_pages <= 2

    def skip_only_one_page(self):
        max_pages = self._source.get_max_pages()
        if max_pages is None:
            return True
        return max_pages <= 1

    def skip_one_or_two(self):
        return self.skip_only_one_page() or self.skip_two_or_less()

    @menus.button(
        "\N{BLACK LEFT-POINTING DOUBLE TRIANGLE WITH VERTICAL BAR}\ufe0f",
        skip_if=skip_one_or_two,
    )
    async def go_to_first_page(self, payload):
        """go to the first page"""
        await self.show_page(0)

    @menus.button("\N{BLACK LEFT-POINTING TRIANGLE}\ufe0f", skip_if=skip_only_one_page)
    async def go_to_previous_page(self, payload):
        """go to the previous page"""
        await self.show_checked_page(self.current_page - 1)

    @menus.button("\N{BLACK RIGHT-POINTING TRIANGLE}\ufe0f", skip_if=skip_only_one_page)
    async def go_to_next_page(self, payload):
        """go to the next page"""
        await self.show_checked_page(self.current_page + 1)

    @menus.button(
        "\N{BLACK RIGHT-POINTING DOUBLE TRIANGLE WITH VERTICAL BAR}\ufe0f",
        skip_if=skip_one_or_two,
    )
    async def go_to_last_page(self, payload):
        """go to the last page"""
        # The call here is safe because it's guarded by skip_if
        await self.show_page(self._source.get_max_pages() - 1)

    @menus.button("\N{BLACK SQUARE FOR STOP}\ufe0f", skip_if=skip_only_one_page)
    async def stop_pages(self, payload):
        """stops the pagination session."""
        await self.message.delete()
        self.stop()


class NormalPageSource(menus.ListPageSource):
    def __init__(self, entries: Sequence[str], *, per_page: int = 1):
        super().__init__(entries, per_page=per_page)

    async def format_page(self, menu, page):
        if isinstance(page, str):
            return page
        else:
            return "\n".join(page)


class ConfirmationMenu(menus.Menu):
    def __init__(
        self,
        to_confirm: str = None,
        *,
        owner_id: int = None,
        send_kwargs=None,
        **kwargs,
    ):
        super().__init__(**kwargs)

        if send_kwargs is None:
            send_kwargs = {}

        self.owner_id = owner_id
        self.send_kwargs = send_kwargs
        self.to_confirm = to_confirm
        self.response = None

    async def send_initial_message(
        self, ctx: commands.Context, channel: discord.TextChannel
    ):
        return await ctx.send(self.to_confirm or "\u200b", **self.send_kwargs)

    def reaction_check(self, payload):
        if payload.message_id != self.message.id:
            return False

        if self.owner_id is not None:
            if payload.user_id not in (self.owner_id, self.bot.owner_id):
                return False

        else:
            if payload.user_id not in (self.bot.owner_id, self._author_id):
                return False

        return payload.emoji in self.buttons

    @menus.button("\N{WHITE HEAVY CHECK MARK}")
    async def do_yes(self, _):
        self.response = True
        self.stop()

    @menus.button("\N{CROSS MARK}")
    async def do_no(self, _):
        self.response = False
        self.stop()

    async def get_response(self, ctx: commands.Context):
        await self.start(ctx, wait=True)
        return self.response
