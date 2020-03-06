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

from random import sample, shuffle
from typing import Optional

from discord.ext import menus


VARIATION_SELECTOR = '\N{VARIATION SELECTOR-16}'

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

LENGTH_5_EMOJI_LIST = EMOJI_LIST[:5]

LEFT_ARROW = '\N{BLACK LEFT-POINTING TRIANGLE}' + VARIATION_SELECTOR
RETURN_ARROW = '\N{LEFTWARDS ARROW WITH HOOK}' + VARIATION_SELECTOR
# these two don't work with names on some machines
YELLOW_CIRCLE = '\U0001f7e1'
GREEN_CIRCLE = '\U0001f7e2'
CROSS_MARK = '\N{CROSS MARK}'


class EmojiGameMenu(menus.Menu):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.value = None
        self.map = self.get_map()

        for button in [menus.Button(e, self.do_emoji_react) for e in self.map]:
            self.add_button(button)

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

class MasterMindMenu(menus.Menu):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.tries = 10
        self.value = None
        self.position = 0
        self.entry = ['X'] * 5
        self.previous_tries = []
        self.code = self.get_code()

        for button in [menus.Button(e, self.do_entry_button) for e in LENGTH_5_EMOJI_LIST]:
            self.add_button(button)

    async def send_initial_message(self, ctx, channel):
        return await ctx.send(
            f'Guess the code to win {ctx.bot.aacoin}s!'
            f'\nYou start with 100 and every guess removes 10.'
            f'\nCode is 4 characters long can you guess it?'
            f'\n\nControls:'
            f'\n1-5 enter that number in the entry box.'
            f'\n{LEFT_ARROW} backspace last number in entry box.'
            f'\n{RETURN_ARROW} enters guess.'
        )

    @property
    def console(self) -> str:
        res = [
            f'Tries left: {self.tries}',
            *self.previous_tries,
            ' '.join(self.entry)
        ]
        return '\n'.join(res)

    async def do_entry_button(self, payload):
        if self.position == 5:
            return await self.ctx.send(
                f'{self.ctx.author.mention}, Max entry reached.',
                delete_after=5,
                escape_mentions=False
            )

        self.entry[self.position] = payload.emoji.name
        self.position += 1
        await self.message.edit(content=self.console)

    @menus.button(LEFT_ARROW, position=menus.Last())
    async def do_backspace(self, _):
        if self.position == 0:
            return

        self.position -= 1
        self.entry[self.position] = 'X'
        await self.message.edit(content=self.console)

    @menus.button(RETURN_ARROW, position=menus.Last(1))
    async def do_enter(self, _):
        if self.position != 5:
            return await self.ctx.send(
                f'{self.ctx.author.mention}, Entry not full.',
                delete_after=5,
                escape_mentions=False)

        if self.entry == self.code:
            self.value = 10 * self.tries
            self.stop()
            return

        dots = self.get_dots()
        self.previous_tries.append(
            f"{' '.join(self.entry)} => {dots}"
        )

        self.entry = ['X'] * 5
        self.position = 0
        self.tries -= 1

        await self.message.edit(content=self.console)

    async def run(self, ctx) -> Optional[int]:
        await self.start(ctx, wait=True)
        return self.value

    @staticmethod
    def get_code():
        copy_emojis = LENGTH_5_EMOJI_LIST.copy()
        shuffle(copy_emojis)
        return ''.join(copy_emojis)

    def get_dots(self):
        res = []
        for guess, correct in zip(self.entry, self.code):
            if guess == correct:
                res.append(GREEN_CIRCLE)

            elif guess in self.code:
                res.append(YELLOW_CIRCLE)

        if not res:
            return CROSS_MARK

        return ''.join(sorted(res))
