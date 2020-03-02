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

import asyncio
import logging
from configparser import ConfigParser

from arcanumbot import ArcanumBot, ROOT, db
from discord.ext.commands import when_mentioned_or

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
"""


async def create_tables():
    async with db.get_database() as connection:
        await connection.executescript(DBSCHEMA.strip())

        await connection.commit()

def main():
    config_file = ROOT / 'arcanum.ini'
    if not config_file.exists():
        config_file.touch()
        config_file.write_text(BASECONFIG.strip())
        exit('Config file made, fill out before running.')

    config = ConfigParser(allow_no_value=True, strict=False)
    config.read(config_file)

    logging.basicConfig(
        format="[%(asctime)s] [%(levelname)s:%(name)s] %(message)s",
        level=logging.INFO
    )

    loop = asyncio.get_event_loop()

    loop.create_task(create_tables())

    bot = ArcanumBot(config,
                     command_prefix=when_mentioned_or(config['general']['prefix']),
                     loop=loop
                     )

    # Todo: make sure to comment
    # bot.dispatch('ready')

    bot.run()


if __name__ == '__main__':
    main()
