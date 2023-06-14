import asyncio
import logging
import os
import pwd
from typing import TYPE_CHECKING, NamedTuple, Optional

import asyncpg
import discord
from discord.ext.commands import CommandError

if TYPE_CHECKING:
    from .bot import ArcanumBot


logger = logging.getLogger(__name__)


DBSCHEMA = """
CREATE TABLE IF NOT EXISTS coins (
    user_id BIGINT NOT NULL,
    coins	BIGINT NOT NULL,
    PRIMARY KEY(user_id)
);

CREATE TABLE IF NOT EXISTS cooldowns (
    command_name TEXT NOT NULL,
    user_id BIGINT NOT NULL,
    PRIMARY KEY(command_name, user_id)
);

CREATE TABLE IF NOT EXISTS purple_hearts (
    user_id BIGINT NOT NULL,
    PRIMARY KEY(user_id)
);
""".strip()


class CoinsEntry(NamedTuple):
    user_id: int
    coins: int


def get_current_username() -> str:
    return pwd.getpwuid(os.getuid()).pw_name


DATABASE_user = get_current_username()
DATABASE_name = "arcanumbot"


class Database:
    def __init__(self):
        self._connection: Optional[asyncpg.Pool] = None
        self._ensured: bool = False
        self._connection_lock = asyncio.Lock()

    async def _ensure_tables(self, pool: asyncpg.Pool):
        # A lock isnt needed here because .connect is already locked
        if self._ensured:
            return

        self._ensured = True

        async with pool.acquire() as connection:
            await connection.execute(DBSCHEMA)

    async def connect(self) -> asyncpg.Pool:
        async with self._connection_lock:
            if self._connection is not None:
                return self._connection

            self._connection = await asyncpg.create_pool(
                user=DATABASE_user, database=DATABASE_name
            )
            assert self._connection is not None
            await self._ensure_tables(self._connection)
            return self._connection

    async def sync_coins_to_discord(self, bot: "ArcanumBot"):
        pool = await self.connect()

        async with pool.acquire() as connection:
            connection: asyncpg.Connection
            coin_rows = await connection.fetch("SELECT * FROM coins;")

            for row in coin_rows:
                user_id = row["user_id"]
                amount = row["coins"]
                try:
                    member = await bot.guild.fetch_member(user_id)
                except discord.NotFound:
                    await self.delete_coin_account(user_id)
                    logger.info(
                        f"Dropped [deleted] account {user_id} from coin db; had {amount} coins"
                    )
                    await bot.logging_channel.send(
                        f"Dropped [deleted] account {user_id} from coin db; had {amount} coins"
                    )
                    continue

                # None means the member has left
                if member is None:
                    await self.delete_coin_account(user_id)
                    logger.info(
                        f"Dropped [left] account {user_id} from coin db; had {amount} coins"
                    )
                    await bot.logging_channel.send(
                        f"Dropped [left] account {user_id} from coin db; had {amount} coins"
                    )

    async def delete_coin_account(self, user_id: int):
        pool = await self.connect()

        async with pool.acquire() as connection:
            await connection.execute("DELETE FROM coins WHERE user_id = $1;", user_id)

        logger.info(f"Deleted coin account {user_id}")

    async def get_coin_balance(self, user_id: int) -> int:
        pool = await self.connect()

        async with pool.acquire() as connection:
            connection: asyncpg.Connection
            row = await connection.fetchrow(
                "SELECT * FROM coins WHERE user_id = $1;", user_id
            )

            if row is not None:
                return row["coins"]

            return 0

    async def get_all_coin_balances(self) -> list[CoinsEntry]:
        pool = await self.connect()

        async with pool.acquire() as connection:
            connection: asyncpg.Connection
            rows = await connection.fetch(
                "SELECT user_id, coins FROM coins ORDER BY coins DESC;"
            )

            result = []
            for row in rows:
                result.append((row["user_id"], row["coins"]))

            return result

    async def set_coins(self, user_id: int, amount: int):
        pool = await self.connect()

        async with pool.acquire() as connection:
            connection: asyncpg.Connection
            await connection.execute(
                "INSERT INTO coins (user_id, coins) VALUES ($1, $2) ON CONFLICT (user_id) DO UPDATE SET coins = EXCLUDED.coins;",
                user_id,
                amount,
            )

        logger.info(f"Set coin account {user_id} to {amount}.")

    async def add_coins(self, user_id: int, amount: int):
        current = await self.get_coin_balance(user_id)
        new_balance = current + amount
        if new_balance.bit_length() >= 64:
            raise CommandError(
                "New balance would be over int64, are you sure you need that many coins?"
            )
        await self.set_coins(user_id, new_balance)
        return new_balance

    async def remove_coins(self, user_id: int, amount: int):
        current = await self.get_coin_balance(user_id)
        new_balance = current - amount
        if new_balance.bit_length() >= 64:
            raise CommandError(
                "New balance would be over int64, are you sure you need that many coins?"
            )
        await self.set_coins(user_id, new_balance)
        return new_balance

    async def set_cooldown(self, user_id: int, command_name: str):
        pool = await self.connect()

        async with pool.acquire() as connection:
            connection: asyncpg.Connection
            await connection.execute(
                "INSERT INTO cooldowns (command_name, user_id) VALUES ($1, $2);",
                command_name,
                user_id,
            )

        logger.info(f"Set cooldown for {user_id} for command {command_name}")

    async def clear_all_cooldowns(self):
        pool = await self.connect()

        async with pool.acquire() as connection:
            connection: asyncpg.Connection
            await connection.execute("DELETE FROM cooldowns;")

        logger.info("All cooldowns cleared")

    async def clear_cooldowns_for_user(self, user_id: int):
        pool = await self.connect()

        async with pool.acquire() as connection:
            connection: asyncpg.Connection
            await connection.execute(
                "DELETE FROM cooldowns WHERE user_id = $1;", user_id
            )

        logger.info(f"Reset cooldowns for {user_id}")

    async def is_on_cooldown(self, command_name: str, user_id: int):
        pool = await self.connect()

        async with pool.acquire() as connection:
            connection: asyncpg.Connection
            row = await connection.fetchrow(
                "SELECT * FROM cooldowns WHERE command_name = $1 AND user_id = $2;",
                command_name,
                user_id,
            )
            return row is not None

    async def set_purple_heart(self, user_id: int):
        pool = await self.connect()

        async with pool.acquire() as connection:
            connection: asyncpg.Connection
            await connection.execute(
                "INSERT INTO purple_hearts (user_id) VALUES ($1);", user_id
            )

        logger.info(f"Set purple heart for {user_id}")

    async def is_purple_heart(self, user_id: int):
        pool = await self.connect()

        async with pool.acquire() as connection:
            connection: asyncpg.Connection
            row = await connection.fetchrow(
                "SELECT * FROM purple_hearts WHERE user_id = $1;", user_id
            )
            return row is not None
