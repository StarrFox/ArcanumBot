import asyncio
import logging
import os
from pathlib import Path

from arcanumbot import ArcanumBot, db

# only works on linux
try:
    import uvloop
except ImportError:
    uvloop = None
else:
    uvloop.install()


DBSCHEMA = """
CREATE TABLE IF NOT EXISTS "coins" (
    "user_id" INTEGER UNIQUE,
    "coins"	INTEGER,
    PRIMARY KEY("user_id")
);

CREATE TABLE IF NOT EXISTS "cooldowns" (
    "command_name" TEXT,
    "user_id" INTEGER,
    PRIMARY KEY("command_name", "user_id")
);

CREATE TABLE IF NOT EXISTS "purple_hearts" (
    "user_id" INTEGER,
    PRIMARY KEY("user_id")
);

CREATE TABLE IF NOT EXISTS "coins_stats" (
    "source" TEXT,
    "user_id" INTEGER,
    "time" TIMESTAMP,
    "amount" INTEGER
);
"""


os.environ["JISHAKU_HIDE"] = "true"
os.environ["JISHAKU_NO_DM_TRACEBACK"] = "true"
os.environ["JISHAKU_NO_UNDERSCORE"] = "true"
os.environ["JISHAKU_RETAIN"] = "true"


async def create_tables():
    async with db.get_database() as connection:
        await connection.executescript(DBSCHEMA.strip())
        await connection.commit()


# TODO: add --secret option for token file
async def _main():
    logging.basicConfig(
        format="[%(asctime)s] [%(levelname)s:%(name)s] %(message)s", level=logging.INFO
    )

    logging.getLogger("discord").setLevel(logging.ERROR)

    loop = asyncio.get_event_loop()

    loop.create_task(create_tables())

    bot = ArcanumBot()

    await bot.load_extension("jishaku")

    with open("discord_token.secret") as fp:
        discord_token = fp.read().strip("\n")

    await bot.start(discord_token)


def main():
    asyncio.run(_main())


if __name__ == "__main__":
    main()
