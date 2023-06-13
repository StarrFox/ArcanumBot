from typing import Sequence, Optional

import discord
from discord.ext import commands, menus


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
        assert self.message is not None
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
        to_confirm: Optional[str] = None,
        *,
        owner_id: Optional[int] = None,
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
