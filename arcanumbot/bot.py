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

import logging
from contextlib import suppress
from asyncio import CancelledError, create_task

import discord
from discord_chan import DiscordChan

from . import db, ConfirmDeleteMenu, MockContext

logger = logging.getLogger(__name__)

class ArcanumBot(DiscordChan):

    aacoin = discord.PartialEmoji(
        name='aacoin',
        id=649846878636212234
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.guild = None
        self.prompt_tasks = []
        self.logging_channel = None

    # # Todo: remove before going into prod
    # async def start(self, *args, **kwargs):
    #     # Todo: uncomment to run
    #     # await super().start(*args, **kwargs)
    #
    #     # Temp replacement for self.connect
    #     import asyncio
    #     while not self.is_closed():
    #         await asyncio.sleep(100)

    async def on_ready(self):
        if self.ready_once:
            return

        self.ready_once = True

        self.guild = self.get_guild(self.config['general'].getint('guild_id'))
        if self.guild:
            self.logging_channel = self.guild.get_channel(self.config['general'].getint('logging_channel_id'))

        await self.validate_coins()

        if self.config['general'].getboolean('load_extensions'):
            self.load_extensions_from_dir('arcanumbot/extensions')

        logger.info(f'Bot ready with {len(self.extensions.keys())} extensions.')

    async def validate_coins(self):
        async with db.get_database() as connection:
            cursor = await connection.execute('SELECT * FROM coins;')
            for user_id, amount in await cursor.fetchall():
                member = self.get_user(user_id)
                if member is not None:
                    pass
                else:
                    self.prompt_tasks.append(
                        create_task(self.prompt_delete(user_id))
                    )

    async def prompt_delete(self, user_id):
        with suppress(CancelledError):
            ctx = MockContext(
                bot=self,
                author=self.get_user(285148358815776768),
                guild=self.guild,
                channel=self.logging_channel
            )

            menu = ConfirmDeleteMenu(user_id)

            response = await menu.get_response(ctx)
            if response is True:
                await self.delete_user_aacoins(user_id)

            else:
                pass

    @staticmethod
    async def delete_user_aacoins(user_id):
        async with db.get_database() as connection:
            await connection.execute('DELETE FROM coins WHERE user_id = (?);', (user_id,))

            await connection.commit()

        logger.info(f'Deleted coin account {user_id}.')

    @staticmethod
    async def get_aacoin_amount(user_id):
        async with db.get_database() as connection:
            cursor = await connection.execute('SELECT coins FROM coins WHERE user_id = (?);', (user_id,))

            return await cursor.fetchone()

    @staticmethod
    async def get_aacoin_lb():
        async with db.get_database() as connection:
            cursor = await connection.execute('SELECT user_id, coins FROM coins ORDER BY coins;')

            return await cursor.fetchall()

    @staticmethod
    async def set_aacoins(user_id, amount):
        async with db.get_database() as connection:
            await connection.execute(
                'INSERT OR REPLACE INTO coins (user_id, coins) VALUES (?, ?);',
                (user_id, amount)
            )

            await connection.commit()

        logger.info(f'Set coin account {user_id} to {amount}.')
