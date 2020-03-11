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

import discord
from discord.ext import commands

from arcanumbot import ArcanumBot

LARGE_RED_CIRCLE = '\N{LARGE RED CIRCLE}'
LARGE_BLUE_DIAMOND = '\N{LARGE BLUE DIAMOND}'
PURPLE_HEART = '\N{PURPLE HEART}'

TARGET_MESSAGE = 651847553633222666
ANNOUNCMENTS = 651673435704918046
GIVEAWAYS = 519182542104952836

logger = logging.getLogger(__file__)


class Events(commands.Cog):

    def __init__(self, bot: ArcanumBot):
        self.bot = bot
        self.reaction_map = {
            LARGE_RED_CIRCLE: self.on_large_red_circle,
            LARGE_BLUE_DIAMOND: self.on_large_blue_diamond,
            PURPLE_HEART: self.on_purple_heart
        }

    # Reaction event

    @commands.Cog.listener('on_raw_reaction_add')
    @commands.Cog.listener('on_raw_reaction_remove')
    async def on_welcome_message_reaction(self, payload: discord.RawReactionActionEvent):
        if payload.message_id != TARGET_MESSAGE:
            return

        if str(payload.emoji) not in (LARGE_RED_CIRCLE,
                                      LARGE_BLUE_DIAMOND,
                                      PURPLE_HEART):
            return

        member = self.bot.guild.get_member(payload.user_id)

        if member:
            await self.reaction_map[str(payload.emoji)](member)

        else:
            msg = f'{payload.user_id} could not be converted to member.'
            logger.critical(msg)

            if self.bot.logging_channel:
                await self.bot.logging_channel(msg)

    async def on_large_red_circle(self, member: discord.Member):
        announcments_role = self.bot.guild.get_role(ANNOUNCMENTS)

        if announcments_role in member.roles:
            await member.remove_roles(announcments_role)

        else:
            await member.add_roles(announcments_role)

    async def on_large_blue_diamond(self, member: discord.Member):
        giveaways_role = self.bot.guild.get_role(GIVEAWAYS)

        if giveaways_role in member.roles:
            await member.remove_roles(giveaways_role)

        else:
            await member.add_roles(giveaways_role)

    async def on_purple_heart(self, member: discord.Member):
        if not await self.bot.is_purple_heart(member.id):
            current = await self.bot.get_aacoin_amount(member.id)

            await self.bot.set_aacoins(member.id, current + 100)
            await self.bot.set_purple_heart(member.id)

def setup(bot: ArcanumBot):
    bot.add_cog(Events(bot))