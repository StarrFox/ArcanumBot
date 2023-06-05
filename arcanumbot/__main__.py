import asyncio
import logging
from configparser import ConfigParser
from pathlib import Path

from arcanumbot import ArcanumBot, db


BASECONFIG = """
[general]
prefix=aa!
# These are filled in so I don't have to get them everytime
coin_mod_role_id=561659914267656202
logging_channel_id=651218048086310932
guild_id=385906835036700672
load_extensions=true

[discord]
token=
"""


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


async def create_tables():
    async with db.get_database() as connection:
        await connection.executescript(DBSCHEMA.strip())
        await connection.commit()


async def _main():
    # Todo: use appdirs config
    config_file = Path("arcanum.ini")
    if not config_file.exists():
        config_file.touch()
        config_file.write_text(BASECONFIG.strip())
        exit("Config file made, fill out before running.")

    config = ConfigParser(allow_no_value=True, strict=False)
    config.read(config_file)

    logging.basicConfig(
        format="[%(asctime)s] [%(levelname)s:%(name)s] %(message)s", level=logging.INFO
    )

    logging.getLogger("discord").setLevel(logging.ERROR)

    loop = asyncio.get_event_loop()

    loop.create_task(create_tables())

    bot = ArcanumBot(config)

    await bot.load_extension("jishaku")

    await bot.start()


def main():
    asyncio.run(_main())


if __name__ == "__main__":
    main()
