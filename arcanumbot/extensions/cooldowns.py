# -*- coding: utf-8 -*-
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

import logging
from datetime import datetime, timedelta

from discord.ext import commands, tasks
from discord.utils import sleep_until

from arcanumbot import ArcanumBot

logger = logging.getLogger(__file__)

class Cooldowns(commands.Cog):
    """Handles cooldowns"""

    def __init__(self, bot: ArcanumBot):
        self.bot = bot

    @tasks.loop(hours=24)
    async def cooldown_cycle(self):
        """
        Resets cooldowns every 24 hours
        """
        await self.bot.clear_cooldowns()

    @cooldown_cycle.before_loop
    async def presence_cycle_before(self):
        await self.bot.wait_until_ready()

        cst = datetime.utcnow() - timedelta(hours=5)
        current_hour = cst.hour
        await sleep_until(cst + timedelta(hours=24 - current_hour))

    @cooldown_cycle.after_loop
    async def presence_cycle_after(self):
        if self.cooldown_cycle.failed():
            logger.critical('Cooldown cycle somehow errored out, restarting.', exc_info=True)
            self.cooldown_cycle.restart()


def setup(bot: ArcanumBot):
    bot.add_cog(Cooldowns(bot))