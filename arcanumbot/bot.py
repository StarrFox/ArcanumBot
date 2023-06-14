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
            command_prefix=kwargs.pop("command_prefix", "aa!"),
            case_insensitive=kwargs.pop("case_insensitive", True),
            max_messages=kwargs.pop("max_messages", 10_000),
            help_command=kwargs.pop("help_command", commands.MinimalHelpCommand()),
            allowed_mentions=kwargs.pop(
                "allowed_mentions",
                discord.AllowedMentions(everyone=False, roles=False, users=False),
            ),
            activity=discord.Activity(
                type=discord.ActivityType.listening,
                name="aa!help",
            ),
            intents=discord.Intents.all(),
            **kwargs,
        )
        self.ready_once = False
        self.add_check(self.only_one_guild)
        self.database = db.Database()

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

    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        if before.content != after.content:
            if after.guild and not isinstance(after.author, discord.Member):
                # Cache bug, after.author is User while before.author is Member
                after.author = await after.guild.fetch_member(after.author.id)

            await self.process_commands(after)

    async def on_ready(self):
        if self.ready_once:
            return

        self.ready_once = True

        await self.validate_coins()

        await self.load_extension("jishaku")

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
        return await self.database.sync_coins_to_discord(self)

    async def delete_user_aacoins(self, user_id):
        return await self.database.delete_coin_account(user_id)

    async def get_aacoin_amount(self, user_id) -> int:
        return await self.database.get_coin_balance(user_id)

    async def get_aacoin_lb(self):
        return await self.database.get_all_coin_balances()

    async def add_aacoins(self, user_id: int, amount: int) -> int:
        return await self.database.add_coins(user_id, amount)

    async def remove_aacoins(self, user_id: int, amount: int) -> int:
        return await self.database.remove_coins(user_id, amount)

    async def set_aacoins(self, user_id: int, amount: int):
        return await self.database.set_coins(user_id, amount)

    async def set_cooldown(self, command_name, user_id):
        return await self.database.set_cooldown(user_id, command_name)

    async def clear_cooldowns(self):
        return await self.database.clear_all_cooldowns()

    async def clear_cooldowns_for_user(self, user_id: int):
        return await self.database.clear_cooldowns_for_user(user_id)

    async def is_on_cooldown(self, command_name: str, user_id: int) -> bool:
        return await self.database.is_on_cooldown(command_name, user_id)

    async def set_purple_heart(self, user_id: int):
        return await self.database.set_purple_heart(user_id)

    async def is_purple_heart(self, user_id) -> bool:
        return await self.database.is_purple_heart(user_id)
