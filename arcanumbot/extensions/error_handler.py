import logging
from datetime import timedelta

import discord
from discord.ext import commands
from humanize import naturaldelta

from arcanumbot import ArcanumBot

logger = logging.getLogger(__name__)


async def on_command_error(ctx: commands.Context[ArcanumBot], error):
    error = getattr(error, "original", error)

    if isinstance(error, commands.CommandNotFound):
        return

    # Bypass checks for owner
    if isinstance(error, commands.CheckFailure):
        if await ctx.bot.is_owner(ctx.author):
            await ctx.reinvoke()
            return

        return await ctx.send("You don't have permission to run that command")

    if isinstance(error, commands.CommandOnCooldown):
        delta = timedelta(seconds=error.retry_after)
        natural = naturaldelta(delta)
        # TODO: use pendulum for this so we can drop the humanize dependency
        return await ctx.send(f"Command on cooldown, retry in {natural}.")
    
    # Reset cooldown when command doesn't finish
    else:
        if ctx.command is not None:
            ctx.command.reset_cooldown(ctx)
            cooldown_message = "; cooldown reset"
        
        else:
            cooldown_message = ""

    if ctx.command is not None:
        logger.error(
            f"Unhandled error in command {ctx.command.name} Invoke message: {ctx.message.content} {error=}"
        )

    await ctx.send(
        f"Unknown error while executing {ctx.command}{cooldown_message}",
        allowed_mentions=discord.AllowedMentions(users=True),
    )


async def setup(bot: ArcanumBot):
    bot.add_listener(on_command_error)


async def teardown(bot: ArcanumBot):
    bot.remove_listener(on_command_error)
