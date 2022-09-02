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
from asyncio import sleep

import pendulum
from discord.ext import commands, tasks

from arcanumbot import ArcanumBot

logger = logging.getLogger(__file__)


class Cooldowns(commands.Cog):
    """Handles cooldowns"""

    def __init__(self, bot: ArcanumBot):
        self.bot = bot
        # for some reason I have to do this, no idea why
        # didn't feel like just making my own thing
        self.cooldown_cycle.before_loop(self.cooldown_cycle_before)
        self.cooldown_cycle.after_loop(self.cooldown_cycle_after)
        if not self.cooldown_cycle.get_task():
            self.cooldown_cycle.start()

    @tasks.loop(hours=24)
    async def cooldown_cycle(self):
        """
        Resets cooldowns every 24 hours
        """
        print("IN COOLDOWN_CYCLE")
        await self.bot.clear_cooldowns()

    # @cooldown_cycle.before_loop
    async def cooldown_cycle_before(self, _):
        cst = pendulum.now("America/Chicago")
        cst_midnight = cst.replace(hour=23, minute=0, second=0, microsecond=0)

        # noinspection PyTypeChecker
        diff = cst.diff(cst_midnight)
        total_seconds = diff.total_seconds()

        logger.info(f"Cooldown cycle sleeping for {total_seconds} seconds.")

        await sleep(total_seconds)

    # @cooldown_cycle.after_loop
    async def cooldown_cycle_after(self, _):
        print("IN COOLDOWN_CYCLE_AFTER")
        if self.cooldown_cycle.failed():
            logger.critical(
                "Cooldown cycle somehow errored out, restarting.", exc_info=True
            )
            self.cooldown_cycle.restart()


async def setup(bot: ArcanumBot):
    await bot.add_cog(Cooldowns(bot))
