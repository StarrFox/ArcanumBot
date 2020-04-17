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
from asyncio import CancelledError, create_task
from contextlib import suppress

import discord
from discord.ext import commands
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
        self.add_check(self.only_one_guild)

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

    async def only_one_guild(self, ctx: commands.Context):
        if not ctx.guild:
            raise commands.NoPrivateMessage(f'Please use commands in {self.guild}.')

        return True

    async def refresh_guild(self):
        self.guild = self.get_guild(self.guild.id)
        return self.guild

    async def validate_coins(self):
        async with db.get_database() as connection:
            cursor = await connection.execute('SELECT * FROM coins;')
            for user_id, amount in await cursor.fetchall():
                member = self.guild.get_member(user_id)
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

            res = await cursor.fetchone()

            if res:
                return res[0]
            else:
                return 0

    @staticmethod
    async def get_aacoin_lb():
        async with db.get_database() as connection:
            cursor = await connection.execute('SELECT user_id, coins FROM coins ORDER BY coins DESC;')

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

    @staticmethod
    async def set_cooldown(command_name, user_id):
        async with db.get_database() as connection:
            await connection.execute(
                'INSERT INTO cooldowns (command_name, user_id) VALUES (?, ?);',
                (command_name, user_id)
            )

            await connection.commit()

        logger.info(f'Set cooldown for {user_id} for command {command_name}.')

    @staticmethod
    async def clear_cooldowns():
        async with db.get_database() as connection:
            await connection.execute('DELETE FROM cooldowns;')

            await connection.commit()

        logger.info('Reset cooldowns.')

    @staticmethod
    async def is_on_cooldown(command_name, user_id) -> bool:
        async with db.get_database() as connection:
            cursor = await connection.execute(
                'SELECT * FROM cooldowns WHERE command_name = (?) AND user_id = (?);',
                (command_name, user_id)
            )

            return bool(await cursor.fetchone())

    @staticmethod
    async def set_purple_heart(user_id):
        async with db.get_database() as connection:
            await connection.execute(
                'INSERT INTO purple_hearts (user_id) VALUES (?);',
                (user_id,)
            )

            await connection.commit()

        logger.info(f'Set purple heart for {user_id}')

    @staticmethod
    async def is_purple_heart(user_id) -> bool:
        async with db.get_database() as connection:
            cursor = await connection.execute(
                'SELECT * FROM purple_hearts WHERE user_id = (?);',
                (user_id,)
            )

            return bool(await cursor.fetchone())
