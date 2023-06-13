import logging
import pathlib
from typing import Union

import discord
from discord.ext import commands

from . import SubContext, constants, db

logger = logging.getLogger(__name__)


class ArcanumBot(commands.Bot):
    aacoin = constants.aacoin_emoji

    def __init__(self, **kwargs):
        super().__init__(
            command_prefix=kwargs.pop("command_prefix", "aa/"),
            case_insensitive=kwargs.pop("case_insensitive", True),
            max_messages=kwargs.pop("max_messages", 10_000),
            help_command=kwargs.pop("help_command", commands.MinimalHelpCommand()),
            allowed_mentions=kwargs.pop(
                "allowed_mentions",
                discord.AllowedMentions(everyone=False, roles=False, users=False),
            ),
            activity=discord.Activity(
                type=discord.ActivityType.listening,
                name=f"aa/help",
            ),
            intents=discord.Intents.all(),
            **kwargs,
        )
        self.ready_once = False
        self.prompt_tasks = []
        self.add_check(self.only_one_guild)

    @property
    def guild(self):
        guild = self.get_guild(constants.guild_id)
        if guild is None:
            raise RuntimeError(f"Target guild could not be found")

        return guild

    @property
    def logging_channel(self):
        logging_channel = self.guild.get_channel(constants.logging_channel_id)
        if logging_channel is None:
            raise RuntimeError(f"Target logging channel could not be found")

        if not isinstance(logging_channel, discord.TextChannel):
            raise RuntimeError(f"Taget logging channel is not of type TextChannel")

        return logging_channel

    async def process_commands(self, message):
        if message.author.bot:
            return

        ctx = await self.get_context(message, cls=SubContext)

        await self.invoke(ctx)

    async def on_ready(self):
        if self.ready_once:
            return

        self.ready_once = True

        await self.validate_coins()

        res = await self.load_extensions_from_dir("arcanumbot/extensions")

        if not res:
            await self.load_extensions_from_dir("extensions")

        logger.info(f"Bot ready with {len(self.extensions.keys())} extensions.")

    async def load_extensions_from_dir(self, path: Union[str, pathlib.Path]) -> int:
        """
        Loads any python files in a directory and it's children
        as extensions

        :param path: Path to directory to load
        :return: Number of extensions loaded
        """
        if not isinstance(path, pathlib.Path):
            path = pathlib.Path(path)

        if not path.is_dir():
            return 0

        before = len(self.extensions.keys())

        extension_names = []

        for subpath in path.glob("**/[!_]*.py"):  # Ignore if starts with _
            parts = subpath.with_suffix("").parts
            if parts[0] == ".":
                parts = parts[1:]

            extension_names.append(".".join(parts))

        for ext in extension_names:
            try:
                await self.load_extension(ext)
            except (commands.errors.ExtensionError, commands.errors.ExtensionFailed):
                logger.exception("Failed loading " + ext)

        return len(self.extensions.keys()) - before

    async def only_one_guild(self, ctx: commands.Context):
        if not ctx.guild:
            raise commands.NoPrivateMessage(f"Please use commands in {self.guild}.")

        if ctx.guild != self.guild:
            raise commands.CheckFailure(f"Please use commands in {self.guild}.")

        return True

    async def validate_coins(self):
        """Resyncs coin db with discord api status"""
        async with db.get_database() as connection:
            cursor = await connection.execute("SELECT * FROM coins;")
            for user_id, amount in await cursor.fetchall():
                try:
                    member = await self.guild.fetch_member(user_id)
                except discord.NotFound:
                    await self.delete_user_aacoins(user_id)
                    logger.info(
                        f"Dropped [deleted] account {user_id} from coin db; had {amount} coins"
                    )
                    await self.logging_channel.send(f"Dropped [deleted] account {user_id} from coin db; had {amount} coins")
                    continue

                # None means the member has left
                if member is None:
                    await self.delete_user_aacoins(user_id)
                    logger.info(
                        f"Dropped [left] account {user_id} from coin db; had {amount} coins"
                    )
                    await self.logging_channel.send(f"Dropped [left] account {user_id} from coin db; had {amount} coins")

    @staticmethod
    async def delete_user_aacoins(user_id):
        async with db.get_database() as connection:
            await connection.execute(
                "DELETE FROM coins WHERE user_id = (?);", (user_id,)
            )

            await connection.commit()

        logger.info(f"Deleted coin account {user_id}.")

    @staticmethod
    async def get_aacoin_amount(user_id) -> int:
        async with db.get_database() as connection:
            cursor = await connection.execute(
                "SELECT coins FROM coins WHERE user_id = (?);", (user_id,)
            )

            res = await cursor.fetchone()

            if res:
                return res[0]
            else:
                return 0

    @staticmethod
    async def get_aacoin_lb():
        async with db.get_database() as connection:
            cursor = await connection.execute(
                "SELECT user_id, coins FROM coins ORDER BY coins DESC;"
            )

            return await cursor.fetchall()

    async def add_aacoins(self, user_id: int, amount: int) -> int:
        balance = await self.get_aacoin_amount(user_id)
        balance += amount
        await self.set_aacoins(user_id, balance)
        return balance

    async def remove_aacoins(self, user_id: int, amount: int) -> int:
        balance = await self.get_aacoin_amount(user_id)
        balance -= amount
        await self.set_aacoins(user_id, balance)
        return balance

    @staticmethod
    async def set_aacoins(user_id, amount):
        async with db.get_database() as connection:
            await connection.execute(
                "INSERT OR REPLACE INTO coins (user_id, coins) VALUES (?, ?);",
                (user_id, amount),
            )

            await connection.commit()

        logger.info(f"Set coin account {user_id} to {amount}.")

    @staticmethod
    async def set_cooldown(command_name, user_id):
        async with db.get_database() as connection:
            await connection.execute(
                "INSERT INTO cooldowns (command_name, user_id) VALUES (?, ?);",
                (command_name, user_id),
            )

            await connection.commit()

        logger.info(f"Set cooldown for {user_id} for command {command_name}.")

    @staticmethod
    async def clear_cooldowns():
        async with db.get_database() as connection:
            await connection.execute("DELETE FROM cooldowns;")

            await connection.commit()

        logger.info("Reset cooldowns.")

    @staticmethod
    async def is_on_cooldown(command_name, user_id) -> bool:
        async with db.get_database() as connection:
            cursor = await connection.execute(
                "SELECT * FROM cooldowns WHERE command_name = (?) AND user_id = (?);",
                (command_name, user_id),
            )

            return bool(await cursor.fetchone())

    @staticmethod
    async def set_purple_heart(user_id):
        async with db.get_database() as connection:
            await connection.execute(
                "INSERT INTO purple_hearts (user_id) VALUES (?);", (user_id,)
            )

            await connection.commit()

        logger.info(f"Set purple heart for {user_id}")

    @staticmethod
    async def is_purple_heart(user_id) -> bool:
        async with db.get_database() as connection:
            cursor = await connection.execute(
                "SELECT * FROM purple_hearts WHERE user_id = (?);", (user_id,)
            )

            return bool(await cursor.fetchone())
