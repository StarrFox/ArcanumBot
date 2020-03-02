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

from random import sample
from typing import Optional

from discord.ext import menus


EMOJI_LIST = [
    '\N{COW FACE}',
    '\N{GRAPES}',
    '\N{POULTRY LEG}',
    '\N{SNOWBOARDER}',
    '\N{POLICE CAR}',
    '\N{REVOLVING HEARTS}',
    '\N{CHEQUERED FLAG}',
    '\N{NO PEDESTRIANS}'
]


class EmojiGameMenu(menus.Menu):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.value = None
        self.map = self.get_map()

    async def send_initial_message(self, ctx, channel):
        return await ctx.send(
            f'React to win a random amount of {ctx.bot.aacoin}s!'
        )

    async def do_emoji_react(self, payload):
        value = self.map[payload.emoji.name]
        self.value = value
        self.stop()

    async def run(self, ctx) -> Optional[int]:
        await self.start(ctx, wait=True)
        return self.value

    @staticmethod
    def get_map() -> dict:
        emojis = sample(EMOJI_LIST, k=5)
        value_sample = sample(range(2, 100 + 1), k=len(emojis))
        return dict(zip(emojis, value_sample))

