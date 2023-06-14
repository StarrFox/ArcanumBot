import logging

import discord
from discord.ext import commands

from arcanumbot import ArcanumBot, constants

LARGE_RED_CIRCLE = "\N{LARGE RED CIRCLE}"
LARGE_BLUE_DIAMOND = "\N{LARGE BLUE DIAMOND}"
PURPLE_HEART = "\N{PURPLE HEART}"

TARGET_MESSAGE = constants.reaction_message
ANNOUNCMENTS = constants.announcments_role
GIVEAWAYS = constants.giveaways_role

logger = logging.getLogger(__name__)


class Events(commands.Cog):
    def __init__(self, bot: ArcanumBot):
        self.bot = bot
        self.reaction_map = {
            LARGE_RED_CIRCLE: self.on_large_red_circle,
            LARGE_BLUE_DIAMOND: self.on_large_blue_diamond,
            PURPLE_HEART: self.on_purple_heart,
        }

    # Reaction event

    @commands.Cog.listener("on_raw_reaction_add")
    @commands.Cog.listener("on_raw_reaction_remove")
    async def on_welcome_message_reaction(
        self, payload: discord.RawReactionActionEvent
    ):
        if payload.message_id != TARGET_MESSAGE:
            return

        if str(payload.emoji) not in (
            LARGE_RED_CIRCLE,
            LARGE_BLUE_DIAMOND,
            PURPLE_HEART,
        ):
            return

        member = await self.bot.guild.fetch_member(payload.user_id)

        if member:
            await self.reaction_map[str(payload.emoji)](member)

        else:
            msg = f"{payload.user_id} could not be converted to member."
            logger.critical(msg)

            await self.bot.logging_channel.send(msg)

    async def on_large_red_circle(self, member: discord.Member):
        announcments_role = self.bot.guild.get_role(ANNOUNCMENTS)

        if announcments_role is None:
            logger.critical(
                f"Announcments role is missing: {member.id} was unable to get the announcment role"
            )
            return

        if announcments_role in member.roles:
            await member.remove_roles(announcments_role)

        else:
            await member.add_roles(announcments_role)

    async def on_large_blue_diamond(self, member: discord.Member):
        giveaways_role = self.bot.guild.get_role(GIVEAWAYS)

        if giveaways_role is None:
            logger.critical(
                f"Giveaways role is missing: {member.id} was unable to get the giveaways role"
            )
            return

        if giveaways_role in member.roles:
            await member.remove_roles(giveaways_role)

        else:
            await member.add_roles(giveaways_role)

    async def on_purple_heart(self, member: discord.Member):
        if not await self.bot.is_purple_heart(member.id):
            current = await self.bot.get_aacoin_amount(member.id)

            await self.bot.set_aacoins(member.id, current + 100)
            await self.bot.set_purple_heart(member.id)


async def setup(bot: ArcanumBot):
    await bot.add_cog(Events(bot))
